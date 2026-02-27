from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LegendWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Легенда"))

    def set_layers(self, layers: list) -> None:
        while self.layout.count() > 1:
            item = self.layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for layer in layers:
            style = layer.style
            color = style.get("color", "#3388cc")
            label = QLabel(f"{layer.name}: {color}")
            self.layout.addWidget(label)
