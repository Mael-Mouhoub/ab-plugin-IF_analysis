from PySide2 import QtWidgets, QtCore,QtGui
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton, QGroupBox, QFileDialog, QMessageBox
from PySide2.QtCore import Signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from collections import defaultdict



bold_font = QtGui.QFont()
bold_font.setBold(True)
bold_font.setPointSize(12)

def header(text):
    label = QtWidgets.QLabel(text)
    label.setFont(bold_font)
    return label

class SimpleMethodTable(QtWidgets.QTableWidget):
    """Tableau simple pour afficher les facteurs de caractérisation d'une méthode."""
    def __init__(self, method_name, data):
        super().__init__(len(data), 5)
        self.setHorizontalHeaderLabels(["Product","Activity","Location","Key", "Factor"])
        self.verticalHeader().setVisible(False)
        self.method_name = method_name
        self.read_only = True
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        # Remplit le tableau avec les données
        for row, (product,activity,location,key, factor) in enumerate(data):
            self.setItem(row, 0, QtWidgets.QTableWidgetItem(product))
            self.setItem(row, 1, QtWidgets.QTableWidgetItem(activity))
            self.setItem(row, 2, QtWidgets.QTableWidgetItem(location))
            self.setItem(row, 3, QtWidgets.QTableWidgetItem(str(key)))
            self.setItem(row, 4, QtWidgets.QTableWidgetItem(str(factor)))
            self.resizeColumnToContents(0)
            self.resizeColumnToContents(1)

    def set_editable(self, editable):
        self.read_only = not editable
        if editable:
            self.setEditTriggers(QtWidgets.QTableWidget.DoubleClicked)
        else:
            self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

class MethodWidget(QtWidgets.QWidget):
    """Fenêtre principale divisée en deux."""
    if_method_signal = Signal(pd.DataFrame)  # Define a signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Characterization Factors")

        # Données améliorées pour chaque méthode : nom, unité, nombre de CF, et données
        excel_path = r"C:\Users\mael.mouhoub\Documents\2-Recherche\5-Git_repositories\ab-plugin-IF_analysis\ab_plugin_IF_analysis\utils\method_input.xlsx"        
        self.methods_data = self.extract_methods_data(excel_path)
        self.if_method_signal.emit(self.methods_data)
        # Widget pour afficher la liste des méthodes (avec colonnes)
        # Layout pour la partie gauche
        self.left_layout = QtWidgets.QVBoxLayout()
        self.methods_tree = QtWidgets.QTreeWidget()
        self.methods_tree.setHeaderLabels(["Method Name", "Unit", "CF Count"])
        self.methods_tree.setColumnCount(3)
        self.methods_tree.setToolTip("Click to select a method.")
        
        self.left_layout.addWidget(header("Impact Categories"))
        self.left_layout.addWidget(self.methods_tree)
        
        self.left_widget = QtWidgets.QWidget()
        self.left_widget.setLayout(self.left_layout)

        # Remplir le QTreeWidget avec les données des méthodes
        for name, info in self.methods_data.items():
            item = QtWidgets.QTreeWidgetItem([name, info["unit"], str(info["cf_count"])])
            self.methods_tree.addTopLevelItem(item)

        # Table des facteurs (à droite)
        self.cf_table = None
        self.current_method = None

        # Checkbox pour activer/désactiver l'édition
        self.editable = QtWidgets.QCheckBox("Edit Characterization Factors")
        self.editable.setToolTip("Make this impact category editable.")
        self.editable.toggled.connect(self.toggle_edit)

        # Label pour le nom de la méthode sélectionnée
        self.method_label = QtWidgets.QLabel("Select a method")

        # Layout pour la partie droite
        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.addWidget(self.method_label)
        self.right_layout.addWidget(self.editable)

        self.right_widget = QtWidgets.QWidget()
        self.right_widget.setLayout(self.right_layout)

        # Layout principal (splitter pour redimensionner)
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.right_widget)
        splitter.setSizes([400, 400])

        # Layout global
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(splitter)

        # Layout import new activity
        self.import_button = QPushButton("import function")
        self.import_button.setFixedWidth(200)
        layout.addWidget(self.import_button)

        self.setLayout(layout)

        # Connexion
        self.methods_tree.itemClicked.connect(self.update_method_view)
        self.import_button.clicked.connect(self.importing_function)


    def update_method_view(self, item, column):
        method_name = item.text(0)
        self.current_method = method_name
        self.method_label.setText(f"Method: {method_name} ({self.methods_data[method_name]['unit']})")

        # Supprime l'ancienne table si elle existe
        if self.cf_table is not None:
            self.right_layout.removeWidget(self.cf_table)
            self.cf_table.deleteLater()

        # Crée une nouvelle table pour la méthode sélectionnée
        self.cf_table = SimpleMethodTable(method_name, self.methods_data[method_name]["data"])
        self.right_layout.insertWidget(3, self.cf_table)

    def toggle_edit(self, editable):
        if self.cf_table is not None:
            self.cf_table.set_editable(editable)
            
    def extract_methods_data(self,excel_path):
            # Lire le fichier Excel
            df = pd.read_excel(excel_path)
            # Initialiser un dictionnaire pour stocker les données
            methods_data = defaultdict(dict)

            # Parcourir les lignes du DataFrame
            for _, row in df.iterrows():
                method = row["method"]
                unit = row["unit"]
                product = row["product"]
                activity = row["activity"]
                location = row["location"]
                key = row["key"]
                factor = row["cf"]

                # Initialiser la structure si la méthode n'existe pas
                if method not in methods_data:
                    methods_data[method] = {
                        "unit": unit,
                        "cf_count": 0,
                        "data": []
                    }

                # Ajouter le couple (substance, factor) à la liste "data"
                methods_data[method]["data"].append((product,activity,location,key,factor))

            # Mettre à jour le nombre de facteurs (cf_count)
            for method in methods_data:
                methods_data[method]["cf_count"] = len(methods_data[method]["data"])

            # Convertir le defaultdict en dict classique
            return dict(methods_data)

    def importing_function(self):
            # 1. Ouvrir une boîte de dialogue pour sélectionner un fichier Excel
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Excel File",
                "",
                "Excel Files (*.xlsx *.xls)"
            )

            if not file_path:
                return  # L'utilisateur a annulé

            # 2. Vérifier que le fichier est bien un .xlsx
            if not file_path.endswith(('.xlsx', '.xls')):
                QMessageBox.warning(self, "Error", "Please select a valid Excel file (.xlsx or .xls).")
                return

            # 3. Extraire les données du fichier
            try:
                extra_methods = self.extract_methods_data(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the file: {str(e)}")
                return

            # 4. Vérifier que le fichier contient des données valides
            if not extra_methods:
                QMessageBox.warning(self, "Error", "The file does not contain valid method data.")
                return

            # 5. Fusionner les nouvelles méthodes avec les existantes
            # (On utilise update pour éviter les doublons)
            for method_name, method_info in extra_methods.items():
                if method_name in self.methods_data:
                    # Si la méthode existe déjà, on fusionne les données
                    self.methods_data[method_name]["data"].extend(method_info["data"])
                    self.methods_data[method_name]["cf_count"] += method_info["cf_count"]
                else:
                    # Sinon, on l'ajoute
                    self.methods_data[method_name] = method_info

            # 6. Mettre à jour le QTreeWidget
            self.update_methods_tree()

            # 7. (Optionnel) Sauvegarder dans un fichier cache
            # self.save_to_cache()  # À implémenter si besoin

            # 8. emit signal
            self.if_method_signal.emit(self.methods_data)

    def update_methods_tree(self):
        """Met à jour le QTreeWidget avec les données actuelles de self.methods_data."""
        self.methods_tree.clear()  # Nettoyer avant de repeupler
        for name, info in self.methods_data.items():
            item = QtWidgets.QTreeWidgetItem([name, info["unit"], str(info["cf_count"])])
            self.methods_tree.addTopLevelItem(item)
