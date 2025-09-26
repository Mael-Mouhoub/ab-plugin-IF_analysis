from PySide2 import QtCore, QtWidgets
from activity_browser.layouts.tabs import PluginTab
from activity_browser.ui.style import horizontal_line, header
from ...widgets.Main_widget import IntermediaryFlowWidget


class RightTab(PluginTab):
    def __init__(self, plugin, parent=None):
        super(RightTab, self).__init__(plugin=plugin, panel="right", parent=parent)
        
        # Initialisation du layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        # Initialisation du widget
        main_widget = IntermediaryFlowWidget()

        # Ajout des éléments au layout
        self.layout.addWidget(header(plugin.infos['name']))
        self.layout.addWidget(horizontal_line())

        #Custom widgets
        self.layout.addWidget(main_widget)

        # Application du layout
        self.setLayout(self.layout)