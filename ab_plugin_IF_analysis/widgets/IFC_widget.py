from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton,QGroupBox
from PySide2.QtCore import Signal, QObject
from .filterable_combobox import FilterableComboBox
import brightway2 as bw
import pandas as pd
import ast
from ..utils.lca_ef_if import lca_ef,lca_if


class CalculWidget(QWidget):
    result_ef_if_signal = Signal(pd.DataFrame,str,str,str)  # Define a signal
    def __init__(self, parent=None):
        super().__init__(parent)

# Layout principal (grand widget)
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Widget interne (plus petit, pour regrouper les éléments)
        inner_widget = QGroupBox("Calculation Parameters")
        inner_layout = QVBoxLayout(inner_widget)

        # --- Database Selection ---
        inner_layout.addWidget(QLabel("Database:"))
        self.db_combo = FilterableComboBox([])
        self.db_combo.setMaximumWidth(1200)
        inner_layout.addWidget(self.db_combo)

        # Ajouter les éléments au layout interne
        inner_layout.addWidget(QLabel("Activity:"))
        self.activity_combo = FilterableComboBox([])
        self.activity_combo.setMaximumWidth(1200)
        inner_layout.addWidget(self.activity_combo)
        # --- IF-EF Layout ---
        if_ef_layout = QHBoxLayout()

        # --- EF Layout ---
        ef_layout = QVBoxLayout()
        ef_layout_include = QHBoxLayout()

        self.include_ef = QCheckBox()
        self.include_ef.setChecked(True)
        ef_layout_include.addWidget(self.include_ef)
        ef_layout_include.addWidget(QLabel("EF Method:"))
        ef_include_widget = QWidget()
        ef_include_widget.setLayout(ef_layout_include)

        self.ef_method_combo = FilterableComboBox([])
        self.ef_method_combo.setMaximumWidth(1200)
        ef_layout.addWidget(ef_include_widget)
        ef_layout.addWidget(self.ef_method_combo)


        ef_widget = QWidget()
        ef_widget.setLayout(ef_layout)
        if_ef_layout.addWidget(ef_widget)

        # --- IF Layout ---
        if_layout = QVBoxLayout()
        if_layout_include = QHBoxLayout()

        self.include_if = QCheckBox()
        self.include_if.setChecked(True)
        if_layout_include.addWidget(self.include_if)
        if_layout_include.addWidget(QLabel("IF Method:"))
        if_include_widget = QWidget()
        if_include_widget.setLayout(if_layout_include)

        self.if_method_combo = FilterableComboBox([])
        self.if_method_combo.setMaximumWidth(1200)
        if_layout.addWidget(if_include_widget)
        if_layout.addWidget(self.if_method_combo)

        if_widget = QWidget()
        if_widget.setLayout(if_layout)
        if_ef_layout.addWidget(if_widget)

        ef_if_widget = QWidget()
        ef_if_widget.setLayout(if_ef_layout)
        inner_layout.addWidget(ef_if_widget)

        # --- Calculate ---
        self.calculation_button = QPushButton("Calculate")
        self.calculation_button.setFixedWidth(200)
        inner_layout.addWidget(self.calculation_button)

        # Ajouter le widget interne au layout principal
        main_layout.addWidget(inner_widget)
        main_layout.addStretch()  # Pour pousser le contenu vers le haut
        
        self.calculation_button.clicked.connect(self.calcultate_if_ef)
        self.db_combo.selection_validated.connect(self.update_activities)
        
        self.init_activity()

    def init_activity(self):
        # --- init database abd activities ---
        self.databases = sorted(bw.databases)
        self.db_combo.set_items(self.databases)
        self.activity_dict = {}
        if self.databases:
            self.update_activities(self.databases[0])
        else:
            self.activity_combo.set_items([])
        # --- init methods ef ---
        list_methods = [str(method) for method in list(bw.methods)]
        top_methods = [
            "('EF v3.0', 'energy resources: non-renewable', 'abiotic depletion potential (ADP): fossil fuels')",
            "('EF v3.0', 'material resources: metals/minerals', 'abiotic depletion potential (ADP): elements (ultimate reserves)')",
        ]
        self.ef_method_combo.set_items(top_methods + sorted(list_methods))
        # # --- init methods if ---
        self.if_panda = {}


    def update_activities(self, db_name):
        """Update the activity ComboBox when a database is selected."""
        if db_name in self.databases and db_name == "biosphere3":
            self.activity_combo.set_items([])
            self.activity_dict = {}
            return

        try:
            db = bw.Database(db_name)
            self.activity_dict = {
                activity.key: f"{activity['name']}, {activity['reference product']}, {activity['location']}"
                for activity in db
            }
            activities = sorted(self.activity_dict.values())
            self.activity_combo.set_items(activities)
        except Exception:
            self.activity_combo.set_items([])
            print(f"Error accessing database {db_name}")

    def calcultate_if_ef(self):
        activity_key = self.get_selected_activity()
        method_ef_name = self.ef_method_combo.current_text()
        method_ef = ast.literal_eval(method_ef_name)
        
        method_if_name = self.if_method_combo.current_text()
        method_if = self.if_panda[method_if_name]["data"] 
        
        print(f"Sélection: Database : {activity_key[0]}, Activity : {activity_key[1]} , Method_ef : {str(method_ef)}, Method_if : {method_if_name}")
        
        if self.include_ef.isChecked() or  method_ef_name == "No method":
            result_ef = lca_ef(activity_key,method_ef)
        else :
            result_ef = None
        if self.include_if.isChecked() or  method_if_name == "No method":
            result_if = lca_if(activity_key,method_if)
        else :
            result_if = None
        result_ef_if = pd.concat([result_ef, result_if], axis=0)
        self.result_ef_if_signal.emit(result_ef_if,self.activity_combo.current_text(),method_ef_name,method_if_name)
        
    def update_if_method(self,if_method_input):
        list_methods_if = if_method_input.keys()
        top_methods = [
        ]
        self.if_method_combo.set_items(top_methods + sorted(list_methods_if))
        self.if_panda = if_method_input
        
    def get_selected_activity(self):
        """Return the selected activity as a tuple (database, key)."""
        activity_text = self.activity_combo.current_text()
        if not activity_text:
            return None

        for key, value in self.activity_dict.items():
            if value == activity_text:
                print(f"Selected Activity: {value} (key: {key})")
                return key
        return None

