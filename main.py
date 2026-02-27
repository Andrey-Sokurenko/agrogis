import logging
import sys

from PySide6.QtWidgets import QApplication

from agro_gis.core.map_model import MapModel
from agro_gis.core.reg_parser import RegParser
from agro_gis.core.vbc_parser import VbcParser
from agro_gis.ui.main_window import MainWindow
from agro_gis.viewmodels.layer_viewmodel import LayerViewModel
from agro_gis.viewmodels.map_viewmodel import MapViewModel


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


if __name__ == "__main__":
    configure_logging()
    app = QApplication(sys.argv)

    map_model = MapModel()
    reg_parser = RegParser()
    vbc_parser = VbcParser()
    map_vm = MapViewModel(map_model, reg_parser, vbc_parser)
    layer_vm = LayerViewModel(map_model)

    window = MainWindow(map_vm, layer_vm)
    window.show()
    sys.exit(app.exec())
