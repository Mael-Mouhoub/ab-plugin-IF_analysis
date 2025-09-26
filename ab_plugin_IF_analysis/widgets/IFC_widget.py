from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton,QGroupBox
from PySide2.QtCore import Signal, QObject
from .filterable_combobox import FilterableComboBox
import brightway2 as bw
import pandas as pd
import ast
from ..utils.lca_ef_if import lca_ef,lca_if


class CalculWidget(QWidget):
    result_ef_if_signal = Signal(pd.DataFrame)  # Define a signal
    def __init__(self, parent=None):
        super().__init__(parent)

# Layout principal (grand widget)
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Widget interne (plus petit, pour regrouper les éléments)
        inner_widget = QGroupBox("Calculation Parameters")
        inner_layout = QVBoxLayout(inner_widget)

        # Ajouter les éléments au layout interne
        inner_layout.addWidget(QLabel("Activity:"))
        self.activity_combo = FilterableComboBox([])
        self.activity_combo.setMaximumWidth(800)
        inner_layout.addWidget(self.activity_combo)

        inner_layout.addWidget(QLabel("EF Method:"))
        self.ef_method_combo = FilterableComboBox([])
        self.ef_method_combo.setMaximumWidth(800)
        inner_layout.addWidget(self.ef_method_combo)

        inner_layout.addWidget(QLabel("IF Method:"))
        self.if_method_combo = FilterableComboBox([])
        self.if_method_combo.setMaximumWidth(800)
        inner_layout.addWidget(self.if_method_combo)

        self.calculation_button = QPushButton("Calculate")
        self.calculation_button.setFixedWidth(200)
        inner_layout.addWidget(self.calculation_button)

        # Ajouter le widget interne au layout principal
        main_layout.addWidget(inner_widget)
        main_layout.addStretch()  # Pour pousser le contenu vers le haut
        
        self.calculation_button.clicked.connect(self.calcultate_if_ef)
        #self.activity_combo.selection_validated.connect(self.get_selected_activity)
        #self.method_combo.selection_validated.connect(self.get_selected_method)
        #self.method_combo.selection_validated.connect(self.get_selected_method
        
        self.init_activity("AEMEL Schropp MS v1 (Eleonora)","Modular structure")

    def init_activity(self,project_name,db_name):
        #init bw and database
        bw.projects.set_current(project_name)
        db = bw.Database(db_name)
        #init activity
        list_activities = [f"{activity['name']}, {activity.key}" for activity in db]
        activities = sorted(list_activities)
        self.activity_combo.set_items(activities)
        #init method ef
        list_methods = [str(method) for method in list(bw.methods)]
        top_methods = [
            "('EF v3.0', 'energy resources: non-renewable', 'abiotic depletion potential (ADP): fossil fuels')",
            "('EF v3.0', 'material resources: metals/minerals', 'abiotic depletion potential (ADP): elements (ultimate reserves)')",
        ]
        self.ef_method_combo.set_items(top_methods + sorted(list_methods))
        #init method if
        excel_path = r"C:\Users\mael.mouhoub\Documents\Recherche\Git_coding\Criticality\Plugin Titouan\plugin_test\utils\method_input.xlsx"        
        self.if_panda = pd.read_excel(excel_path)
        self.update_if_method(self.if_panda)

    def calcultate_if_ef(self):
        activity_text = self.activity_combo.current_text()
        activity_key_str = activity_text.split('(', 1)[1].rstrip(')')
        activity_key = ast.literal_eval(activity_key_str)
        
        method_ef = ast.literal_eval(self.ef_method_combo.current_text())
        
        #method_if = pd.read_excel("plugin_test/utils/method_input.xlsx") #"No method" #ast.literal_eval(self.method_combo.current_text())
        method_if_name = self.if_method_combo.current_text()
        method_if = self.if_panda[self.if_panda["method"] == method_if_name]
        
        print(f"Sélection: Database : {activity_key[0]}, Activity : {activity_key[1]} , Method_ef : {str(method_ef)}, Method_if : {method_if_name}")
        
        result_ef = lca_ef(activity_key,method_ef)
        result_if = lca_if(activity_key,method_if)
        result_ef_if = pd.concat([result_ef, result_if], axis=0)
        self.result_ef_if_signal.emit(result_ef_if)
        
    def update_if_method(self,if_method_input):
        list_methods_if = list(if_method_input["method"].unique())
        self.if_method_combo.set_items(sorted(list_methods_if))
        #self.if_panda = if_method_input
        


