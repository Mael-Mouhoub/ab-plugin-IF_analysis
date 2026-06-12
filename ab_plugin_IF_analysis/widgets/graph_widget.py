from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton,QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

class MplCanvas(FigureCanvas):
    """Canvas pour afficher un graphique matplotlib dans une fenêtre PySide2."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        
class SimpleMethodTable(QtWidgets.QTableWidget):
    """Tableau simple pour afficher les facteurs de caractérisation d'une méthode."""
    def __init__(self,header):
        super().__init__(0, len(header))  # Initialiser avec 0 lignes, 2 colonnes
        self.setHorizontalHeaderLabels(header)
        self.verticalHeader().setVisible(False)
        self.read_only = True
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

class GraphWidget(QtWidgets.QWidget):
    """Fenêtre affichant un histogramme à barres empilées (une seule barre)."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Critical Raw Material Footprint ")
        self.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout()
        # Créer le canvas matplotlib
        self.canvas = MplCanvas(self, width=12, height=10, dpi=100)
        self.tab = SimpleMethodTable(["crm","product","inventory" ,"cf","score"])
        self.tab2 = SimpleMethodTable(["crm","crm_inventory" ,"cf_unitary","score"])
        #Set tab layout
        self.tab_layout = QHBoxLayout()
        self.tab_layout.addWidget(self.tab2)
        self.tab_layout.addWidget(self.tab)
        self.tab_widget = QWidget()
        self.tab_widget.setLayout(self.tab_layout)
        #Set main layout
        layout.addWidget(self.canvas)
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    

    def plot_stacked_bar(self, df,act_name,if_method_name):
        """Affiche une barre empilée des 10 plus grands lca_score par activité."""
        self.canvas.axes.clear()  # Efface l'ancien graphique
        # update changer uniquement la vue graph en agreegant les score des meme crm en mettant comme nom le crm et le displayant 
        # Aggregate lca_score by crm and sum
        aggregated_df = df.groupby(['crm', 'type'], as_index=False)['lca_score'].sum() 
        
        # Trier le DataFrame par lca_score décroissant et prendre les 10 premiers
        # top_10 = df.nlargest(10, 'lca_score') # old
        top_10 = aggregated_df.nlargest(10, 'lca_score') # new
        # Extraire les activités et scores
        Flows = top_10['crm'].values # new
        scores = top_10['lca_score'].values
        Types = top_10['type'].values # old

        # Couleurs pour chaque section de la barre empilée
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0',
                '#ffb3e6', '#ff6666', '#66ffcc', '#ff99cc', '#99ccff']
        
        # Définir la taille de police pour le titre et les axes
        title_fontsize = 22  # Taille du titre
        label_fontsize = 20  # Taille des labels (axes)
        legend_fontsize = 20  # Taille de la légende

        # Initialiser la position de départ pour l'empilement
        bottom = 0
        bottom_if = 0
        bars = []
        categories = ['IF']
        x_pos = range(len(categories))  # [0, 1, 2]

        for i, (product, score, type_flow) in enumerate(zip(Flows, scores, Types)):
            # # Barre "Total" (toujours à x=0)
            # bar = self.canvas.axes.bar(x_pos[0], [score], bottom=bottom, color=colors[i], label=product)
            # bottom += score
            # bars.append(bar)

            if type_flow == "IF":
                # Barre "IF" (toujours à x=1)
                bar_if = self.canvas.axes.bar(x_pos[0], [score], bottom=bottom_if, color=colors[i], label=product)
                bottom_if += score
                bars.append(bar_if)

            # if type_flow == "EF":
            #     # Barre "EF" (toujours à x=2)
            #     bar_ef = self.canvas.axes.bar(x_pos[2], [score], bottom=bottom_ef, color=colors[i])
            #     bottom_ef += score
            #     bars.append(bar_ef)
                
        # # Score total pour "Total"
        # self.canvas.axes.text(
        #     0, bottom + 0.02 * bottom,  # Position x=0 (barre "Total"), y=légèrement au-dessus
        #     f"{bottom:.2e}",
        #     ha='center', va='bottom', fontsize=10, fontweight='bold'
        # )

        # Score total pour "IF"
        self.canvas.axes.text(
            0, bottom_if + 0.02 * bottom_if,  # Position x=1 (barre "IF")
            f"{bottom_if:.2e}",
            ha='center', va='bottom', fontsize=20, fontweight='bold'
        )

        # # Score total pour "EF"
        # self.canvas.axes.text(
        #     2, bottom_ef + 0.02 * bottom_ef,  # Position x=2 (barre "EF")
        #     f"{bottom_ef:.2e}",
        #     ha='center', va='bottom', fontsize=10, fontweight='bold'
        # )
        
        # Définir les labels de l'axe x et leur ordre
        self.canvas.axes.set_xticks(x_pos)
        self.canvas.axes.set_xticklabels([act_name])
        self.canvas.axes.tick_params(axis='x',labelsize=16,)
        self.canvas.axes.set_ylabel(if_method_name, fontsize=label_fontsize)
        self.canvas.axes.set_title(f"Critical raw material footprint  : \n FU : X {act_name}; IF method : {if_method_name}",fontsize=title_fontsize, pad=35)  # Espacement supplémentaire sous le titre
        # Légende à l'extérieur, à droite
        self.canvas.axes.legend(
            loc='upper left',
            bbox_to_anchor=(1, 1),  # (1, 1) = coin supérieur droit, juste à l'extérieur
            fontsize=legend_fontsize,
            reverse=True
        )
        # Ajuste la taille pour laisser de la place à la légende
        #self.canvas.figure.tight_layout(rect=[0, 0, 0.85, 1])
        #self.canvas.axes.legend(loc='upper right')  # Afficher la légende
        self.canvas.figure.tight_layout()  # Ajuste la taille
        self.canvas.draw()


    def update_graph(self,df,act_name,if_method_name) :
        # Générer le graphique
        self.plot_stacked_bar(df,act_name,if_method_name)
        
    def update_tab(self,df,act_name,if_method_name):
        # Effacer le contenu actuel
        self.tab.setRowCount(0)
        # Calculate the total lca_score sum
        total_lca = df['lca_score'].sum()

        aggregated_df = df.groupby(['crm', 'type', 'cf_unitaire'], as_index=False)['lca_score'].sum() 

        # Define the 2% cutoff
        cutoff_1 = 0 * total_lca
        cutoff_2 = 0 * total_lca

        # Filter rows where lca_score >= 2% of total
        filtered_df = df[df['lca_score'] >= cutoff_1]
        filtered_aggregated_df = aggregated_df[aggregated_df['lca_score'] >= cutoff_2]

        # Sort by crm (ascending) and then by lca_score (descending)
        top_crm = filtered_df.sort_values(
            by=['crm', 'lca_score'],
            ascending=[True, False]  # Sort crm ascending, lca_score descending
        ).reset_index(drop=True)

        # Sort by crm (ascending) and then by lca_score (descending)
        filtered_aggregated_df = filtered_aggregated_df.sort_values(
            by=['lca_score'],
            ascending=[False]  # Sort crm ascending, lca_score descending
        ).reset_index(drop=True)

        # Ajouter les lignes nécessaires
        self.tab.setRowCount(len(top_crm))
        # Remplir le tableau
        for index, row in top_crm.iterrows():
            self.tab.setItem(index, 0, QtWidgets.QTableWidgetItem(row["crm"]))
            self.tab.setItem(index, 1, QtWidgets.QTableWidgetItem(row["product"]))
            self.tab.setItem(index, 2, QtWidgets.QTableWidgetItem(f"{row['inventory']:.2e}"))  
            self.tab.setItem(index, 3, QtWidgets.QTableWidgetItem(f"{row['cf']:.2e}"))       
            self.tab.setItem(index, 4, QtWidgets.QTableWidgetItem(f"{row['lca_score']:.2e}")) 
        
        self.tab2.setRowCount(len(filtered_aggregated_df))
        for index, row in filtered_aggregated_df.iterrows():
            self.tab2.setItem(index, 0, QtWidgets.QTableWidgetItem(row["crm"]))
            self.tab2.setItem(index, 1, QtWidgets.QTableWidgetItem(f"{(row['lca_score']/row['cf_unitaire']):.2e}"))  # Inventaire en kg de ressource
            self.tab2.setItem(index, 2, QtWidgets.QTableWidgetItem(f"{row['cf_unitaire']:.2e}")) # cf pour 1 kg      
            self.tab2.setItem(index, 3, QtWidgets.QTableWidgetItem(f"{row['lca_score']:.2e}")) 

            # Ajuster la largeur des colonnes au contenu
        self.tab.resizeColumnsToContents()