from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from agro_gis.core.encoding_utils import MANUAL_CHOICES
from agro_gis.core.exceptions import EncodingDetectionError
from agro_gis.ui.layer_panel import LayerPanel
from agro_gis.ui.legend_widget import LegendWidget
from agro_gis.ui.map_widget import MapWidget
from agro_gis.viewmodels.layer_viewmodel import LayerViewModel
from agro_gis.viewmodels.map_viewmodel import MapViewModel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, map_vm: MapViewModel, layer_vm: LayerViewModel) -> None:
        super().__init__()
        self.map_vm = map_vm
        self.layer_vm = layer_vm

        self.setWindowTitle("Agro GIS")
        self.resize(1200, 800)
        self.setAcceptDrops(True)

        container = QWidget()
        self.setCentralWidget(container)
        root = QHBoxLayout(container)

        left_panel = QVBoxLayout()
        btn_reg = QPushButton("Загрузить карту (.reg)")
        btn_vbc = QPushButton("Загрузить точки (.vbc)")
        btn_zoom_in = QPushButton("+")
        btn_zoom_out = QPushButton("-")

        btn_reg.clicked.connect(self.open_reg)
        btn_vbc.clicked.connect(self.open_vbc)
        btn_zoom_in.clicked.connect(lambda: self.map_widget.zoom(0.8))
        btn_zoom_out.clicked.connect(lambda: self.map_widget.zoom(1.25))

        self.layer_panel = LayerPanel()
        self.legend_widget = LegendWidget()

        left_panel.addWidget(btn_reg)
        left_panel.addWidget(btn_vbc)
        left_panel.addWidget(btn_zoom_in)
        left_panel.addWidget(btn_zoom_out)
        left_panel.addWidget(self.layer_panel)
        left_panel.addWidget(self.legend_widget)

        self.map_widget = MapWidget(self.map_vm.map_model)
        root.addLayout(left_panel, 1)
        root.addWidget(self.map_widget, 3)

        status = QStatusBar()
        self.setStatusBar(status)

        self.map_vm.layers_changed.connect(self.refresh)
        self.map_vm.error_occurred.connect(self._show_critical)

        self.layer_panel.visibility_changed.connect(self.layer_vm.set_layer_visibility)
        self.layer_panel.remove_requested.connect(self.layer_vm.remove_layer)
        self.layer_panel.move_up_requested.connect(lambda idx: self.layer_vm.move_layer(idx, idx - 1))
        self.layer_panel.move_down_requested.connect(lambda idx: self.layer_vm.move_layer(idx, idx + 1))

        self.layer_vm.layers_changed.connect(self.refresh)
        self.map_widget.cursor_coordinates_changed.connect(self._update_status_coords)

    def open_reg(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open .reg", "", "REG files (*.reg)")
        if file_path:
            self._load_file(Path(file_path))

    def open_vbc(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open .vbc", "", "VBC files (*.vbc)")
        if file_path:
            self._load_file(Path(file_path))

    def _load_file(self, path: Path) -> None:
        suffix = path.suffix.lower()
        try:
            if suffix == ".reg":
                self.map_vm.load_reg(str(path))
            elif suffix == ".vbc":
                self.map_vm.load_vbc(str(path))
            else:
                QMessageBox.warning(self, "Unsupported", "Поддерживаются только .reg и .vbc файлы")
        except EncodingDetectionError as exc:
            logger.warning("Auto encoding detection failed for %s: %s", path, exc)
            encoding = self._ask_encoding()
            if not encoding:
                return
            try:
                if suffix == ".reg":
                    self.map_vm.load_reg(str(path), encoding)
                elif suffix == ".vbc":
                    self.map_vm.load_vbc(str(path), encoding)
            except Exception as retry_exc:
                logger.error("Load failed after manual encoding selection", exc_info=True)
                QMessageBox.critical(self, "Ошибка", str(retry_exc))
        except Exception as exc:
            logger.error("Load failed", exc_info=True)
            QMessageBox.critical(self, "Ошибка", str(exc))

    def refresh(self) -> None:
        self.map_widget.render_layers()
        self.layer_panel.set_layers(self.map_vm.map_model.layers)
        self.legend_widget.set_layers(self.map_vm.map_model.layers)

    def _show_critical(self, message: str) -> None:
        QMessageBox.critical(self, "Ошибка", message)

    def _update_status_coords(self, lat: float, lon: float) -> None:
        self.statusBar().showMessage(f"lat={lat:.6f}, lon={lon:.6f}")

    def _ask_encoding(self) -> str | None:
        encoding, ok = QInputDialog.getItem(self, "Выбор кодировки", "Кодировка:", MANUAL_CHOICES, 0, False)
        return encoding if ok else None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() not in {".reg", ".vbc"}:
                QMessageBox.warning(self, "Unsupported", f"Неподдерживаемый файл: {path.name}")
                continue
            self._load_file(path)
