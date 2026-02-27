from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LayerPanel(QWidget):
    visibility_changed = Signal(int, bool)
    remove_requested = Signal(int)
    move_up_requested = Signal(int)
    move_down_requested = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.list_widget = QListWidget()
        self.list_widget.itemChanged.connect(self._on_item_changed)

        btn_remove = QPushButton("Удалить")
        btn_up = QPushButton("Вверх")
        btn_down = QPushButton("Вниз")

        btn_remove.clicked.connect(self._emit_remove)
        btn_up.clicked.connect(self._emit_up)
        btn_down.clicked.connect(self._emit_down)

        row = QHBoxLayout()
        row.addWidget(btn_remove)
        row.addWidget(btn_up)
        row.addWidget(btn_down)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addLayout(row)

    def set_layers(self, layers: list) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for layer in layers:
            item = QListWidgetItem(layer.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if layer.visible else Qt.Unchecked)
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        idx = self.list_widget.row(item)
        self.visibility_changed.emit(idx, item.checkState() == Qt.Checked)

    def _emit_remove(self) -> None:
        idx = self.list_widget.currentRow()
        if idx >= 0:
            self.remove_requested.emit(idx)

    def _emit_up(self) -> None:
        idx = self.list_widget.currentRow()
        if idx > 0:
            self.move_up_requested.emit(idx)

    def _emit_down(self) -> None:
        idx = self.list_widget.currentRow()
        if 0 <= idx < self.list_widget.count() - 1:
            self.move_down_requested.emit(idx)
