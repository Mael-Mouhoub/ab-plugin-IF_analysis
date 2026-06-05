from PySide2.QtWidgets import QTabWidget, QVBoxLayout, QWidget
from .IFC_widget import CalculWidget
from .IFM_widget import MethodWidget
from .graph_widget import GraphWidget

class IntermediaryFlowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Intermediary flow plugin")

        # Layout principal
        layout = QVBoxLayout(self)

        # Création du QTabWidget
        self.tab_widget = QTabWidget()

        # Création des widgets pour chaque onglet
        self.calcul_widget = CalculWidget()
        self.if_method = MethodWidget()
        self.graph_result = GraphWidget()

        # Ajout des onglets
        self.add_tab("Advanced LCA Setup", self.calcul_widget)
        self.add_tab("Intermediary flow method", self.if_method)
        self.add_tab("LCA result", self.graph_result)

        # Ajout du QTabWidget au layout
        layout.addWidget(self.tab_widget)

        # Connexion des signaux
        self.calcul_widget.result_ef_if_signal.connect(self.graph_result.update_graph)
        self.calcul_widget.result_ef_if_signal.connect(self.graph_result.update_tab)
        self.if_method.if_method_signal.connect(self.calcul_widget.update_if_method)
        
        # Émettre le signal après que toutes les connexions soient établies
        self.if_method.emit_initial_signal()

    def add_tab(self, title, widget_input):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(widget_input)
        self.tab_widget.addTab(tab, title)
