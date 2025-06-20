# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 17:38:53 2024

@author: toussaij
"""

# Importation des bibliothèques nécessaires
import sys  # Pour accéder aux arguments et fonctions du système
import numpy as np  # Pour les opérations mathématiques et les tableaux
from scipy.integrate import solve_ivp  # Pour la résolution d'équations différentielles
from matplotlib.figure import Figure  # Pour créer des figures matplotlib
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas, 
    NavigationToolbar2QT as NavigationToolbar)  # Pour intégrer matplotlib dans PyQt5
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QTabWidget, 
    QVBoxLayout, 
    QWidget, 
    QSplitter, 
    QTableWidget, 
    QTableWidgetItem, 
    QHeaderView, 
    QHBoxLayout, 
    QMessageBox)  # Importation des widgets PyQt5
from PyQt5.QtCore import Qt  # Pour les constantes de Qt

# Liste des méthodes de résolution pour solve_ivp
methods = ['LSODA', 'BDF', 'Radau', 'DOP853']

class Params:
    """Classe Params pour stocker les paramètres du modèle.
    
    Attributs:
        tau (float): Temps caractéristique.
        beta_q (float): Facteur d'échelle pour le courant ionique.
        I0 (float): Courant initial.
        Is (float): Courant de saturation.
        Rs (float): Résistance série.
        C (float): Capacité.
        tf (float): Temps final de simulation.
        period (float): Période du signal trapézoïdal.
        rise_time (float): Temps de montée du signal.
        fall_time (float): Temps de descente du signal.
        amplitude (float): Amplitude du signal.
    """
    tau: float = 5  # Temps caractéristique de décroissance
    beta_q: float = 1  # Facteur d'échelle pour le courant ionique
    I0: float = 10.0  # Courant initial
    Is: float = 1  # Courant de saturation
    Rs: float = 0.1  # Résistance série
    C: float = 0.01  # Capacité
    tf: float = 200  # Temps final de simulation
    period: float = 20  # Période du signal trapézoïdal
    rise_time: float = 5  # Temps de montée du signal
    fall_time: float = 5  # Temps de descente du signal
    amplitude: float = 5  # Amplitude du signal

class Q_ODE:
    """Classe Q_ODE pour définir le système d'équations différentielles.
    
    Cette classe modélise un système d'équations différentielles en utilisant 
    les paramètres définis dans la classe Params.
    
    Méthodes:
        __call__(t, unk): Calcule les dérivées des variables d'état au temps t.
        trapezoidal_signal(t): Génère un signal trapézoïdal en fonction du temps.
    """
    def __init__(self, params: Params):
        """Initialise le système d'équations différentielles avec les paramètres donnés."""
        self.params = params  # Stocke les paramètres dans l'instance

    def __call__(self, t, unk):
        """Calcule les dérivées des variables d'état au temps t.
        
        Args:
            t (float): Temps actuel.
            unk (list): Liste contenant les valeurs actuelles de Iion et u.
        
        Returns:
            list: Liste contenant les dérivées dIion_dt et du_dt.
        """
        # Récupération des paramètres du modèle
        tau, beta_q, I0, Is, Rs, C = (self.params.tau, self.params.beta_q, self.params.I0, self.params.Is, self.params.Rs, self.params.C)
        Vapp = self.trapezoidal_signal(t)  # Calcul du signal appliqué au temps t
        Iion, u = unk  # Valeurs actuelles de Iion et u
        abs_u = np.abs(u)  # Valeur absolue de u
        Ielec = np.sign(u) * Is * (np.exp(beta_q * abs_u) - 1.0)  # Calcul du courant électronique
        dIion_dt = -Iion / tau + I0 / (tau * (1.0 + np.exp(beta_q * abs_u)))  # Calcul de la dérivée de Iion
        du_dt = (Vapp - u) / (Rs * C) - Ielec / C - Iion / C  # Calcul de la dérivée de u
        return [dIion_dt, du_dt]  # Retourne les dérivées

    def trapezoidal_signal(self, t):
        """Génère un signal trapézoïdal en fonction du temps.
        
        Args:
            t (float): Temps actuel.
        
        Returns:
            float: Valeur du signal trapézoïdal au temps t.
        """
        # Récupération des paramètres du signal
        period, rise_time, fall_time, amplitude = (self.params.period, self.params.rise_time, self.params.fall_time, self.params.amplitude)
        plateau_time = period - rise_time - fall_time  # Temps du plateau
        t_mod = t % period  # Temps modulo la période
        # Calcul du signal en fonction du temps dans la période
        if 0 <= t_mod < rise_time:
            return (amplitude / rise_time) * t_mod
        elif rise_time <= t_mod < rise_time + plateau_time:
            return amplitude
        elif rise_time + plateau_time <= t_mod < period:
            return amplitude - (amplitude / fall_time) * (t_mod - rise_time - plateau_time)
        return 0

class MplCanvas(FigureCanvas):
    """Classe MplCanvas pour créer une zone de dessin avec Matplotlib.
    
    Cette classe fournit un canevas de dessin pour l'affichage des graphiques
    dans l'interface Qt.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """Initialise le canevas de dessin avec les dimensions spécifiées."""
        fig = Figure(figsize=(width, height), dpi=dpi)  # Crée une nouvelle figure
        self.axes = fig.add_subplot(111)  # Ajoute un subplot à la figure
        super().__init__(fig)  # Initialise la classe parente

class CustomNavigationToolbar(NavigationToolbar):
    """Classe CustomNavigationToolbar pour personnaliser la barre d'outils de navigation.

    Cette classe redéfinit la méthode de sauvegarde pour inclure un nom de fichier par défaut.
    """
    def __init__(self, canvas, parent, method_name):
        super().__init__(canvas, parent)
        self.method_name = method_name  # Stocke le nom de la méthode utilisée pour la solution

    def save_figure(self, *args):
        """Redéfinit la fonction de sauvegarde pour inclure un nom de fichier par défaut."""
        default_filename = f"{self.method_name}.png"  # Nom de fichier par défaut
        print('snapshot file : ', default_filename)
        self.canvas.figure.savefig(default_filename)  # Sauvegarde la figure avec le nom par défaut
        QMessageBox.information(self, "Information", f"Snapshot saved in {default_filename}")

class TabWidget(QMainWindow):
    """Classe TabWidget pour créer l'interface utilisateur avec des onglets.
    
    Cette classe crée une fenêtre principale avec des onglets pour afficher 
    les résultats des différentes méthodes de résolution.
    """
    def __init__(self):
        """Initialise la fenêtre principale avec des onglets pour chaque méthode."""
        super().__init__()  # Initialise la classe parente
        self.setWindowTitle("The Q-integrator")  # Définit le titre de la fenêtre
        self.setGeometry(100, 100, 1000, 600)  # Définit la position et la taille de la fenêtre
        tab_widget = QTabWidget()  # Crée un widget d'onglets
        self.setCentralWidget(tab_widget)  # Définit le widget d'onglets comme widget central
        tabs = [QWidget() for _ in methods]  # Crée un widget pour chaque méthode
        for tab, method in zip(tabs, methods):  # Pour chaque méthode et onglet
            label = f"sol_{method}"  # Crée un label pour l'onglet
            tab_widget.addTab(tab, label)  # Ajoute l'onglet au widget d'onglets
            self.create_tab_layout(tab, solutions[method], method)  # Crée la disposition de l'onglet

    def create_tab_layout(self, tab, solution, method):
        """Crée la disposition de l'onglet pour afficher les résultats.
        
        Args:
            tab (QWidget): Widget de l'onglet.
            solution (OdeSolution): Solution du système d'équations.
            method (str): Nom de la méthode de résolution.
        """
        layout = QVBoxLayout(tab)  # Crée une disposition verticale pour l'onglet
        splitter = QSplitter(Qt.Horizontal)  # Crée un séparateur horizontal
        table_widget = self.create_table_widget(solution)  # Crée un widget tableau
        plot_widget = self.create_plot_widget(solution, table_widget, method)  # Crée un widget de graphique
        splitter.addWidget(table_widget)  # Ajoute le tableau au séparateur
        splitter.addWidget(plot_widget)  # Ajoute le graphique au séparateur
        layout.addWidget(splitter)  # Ajoute le séparateur à la disposition de l'onglet

    def create_table_widget(self, solution):
        """Crée un widget tableau pour afficher les données de la solution.
        
        Args:
            solution (OdeSolution): Solution du système d'équations.
        
        Returns:
            QTableWidget: Widget tableau rempli avec les données de la solution.
        """
        table_widget = QTableWidget()  # Crée un widget tableau
        table_widget.setColumnCount(3)  # Définit le nombre de colonnes
        table_widget.setRowCount(len(solution.t))  # Définit le nombre de lignes
        table_widget.setHorizontalHeaderLabels(['t', 'Iion', 'u'])  # Définit les labels des colonnes
        # Remplit le tableau avec les données de la solution
        for i, (t, Iion, u) in enumerate(zip(solution.t, solution.y[0], solution.y[1])):
            t_item = QTableWidgetItem(f"{t:.5f}")  # Crée un item pour le temps
            Iion_item = QTableWidgetItem(f"{Iion:.5f}")  # Crée un item pour Iion
            u_item = QTableWidgetItem(f"{u:.5f}")  # Crée un item pour u
            for item in [t_item, Iion_item, u_item]:  # Pour chaque item
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Rend l'item non éditable
            table_widget.setItem(i, 0, t_item)  # Ajoute l'item du temps à la ligne i
            table_widget.setItem(i, 1, Iion_item)  # Ajoute l'item de Iion à la ligne i
            table_widget.setItem(i, 2, u_item)  # Ajoute l'item de u à la ligne i
        table_widget.resizeColumnsToContents()  # Redimensionne les colonnes pour contenir le texte
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Ajuste la taille des colonnes
        return table_widget  # Retourne le widget tableau

    def create_plot_widget(self, solution, table_widget, method):
        """Crée un widget de graphique pour afficher les résultats de la simulation.
        
        Args:
            solution (OdeSolution): Solution du système d'équations.
            table_widget (QTableWidget): Widget tableau associé.
            method (str): Nom de la méthode de résolution.
        
        Returns:
            QWidget: Widget contenant le graphique.
        """
        plot_widget = QWidget()  # Crée un widget pour le graphique
        layout = QVBoxLayout(plot_widget)  # Crée une disposition verticale pour le widget
        sc = MplCanvas(self, width=5, height=4, dpi=100)  # Crée un canevas de dessin matplotlib
        self.current_line = None  # Ajoute un attribut pour stocker la ligne verticale
        
        if solution.success:  # Si la solution a été trouvée avec succès
            # Trace les graphiques de Iion(t) et u(t)
            sc.axes.plot(solution.t, solution.y[0], label='Iion(t)', color='r', picker=5)
            sc.axes.plot(solution.t, solution.y[1], label='u(t)', color='b', picker=5)
            sc.axes.set_xlabel('t')  # Définit le label de l'axe des x
            sc.axes.set_ylabel('Iion(t) u(t)')  # Définit le label de l'axe des y
            sc.axes.set_xlim(t_min, t_max)  # Définit les limites de l'axe des x
            sc.axes.set_ylim(y_min, y_max)  # Définit les limites de l'axe des y
            sc.axes.legend()  # Affiche la légende
            sc.axes.grid()  # Affiche une grille
            toolbar = CustomNavigationToolbar(sc, self, method)  # Utilise la barre d'outils personnalisée
            # Connecte l'événement de clic sur le graphique à une fonction
            table_widget.itemSelectionChanged.connect(lambda: self.on_table_click(sc, table_widget))
            # Connecte l'événement de clic sur le graphique à une fonction
            sc.mpl_connect('button_press_event', lambda event: self.onclick(event, solution, table_widget))
            layout.addWidget(toolbar)  # Ajoute la barre d'outils à la disposition
            layout.addWidget(sc)  # Ajoute le canevas de dessin à la disposition
        return plot_widget  # Retourne le widget du graphique

    def on_table_click(self, sc, table_widget):
        """Gère les événements de clic sur le tableau.
        
        Args:
            sc (MplCanvas): Le canevas de dessin pour le graphique.
            table_widget (QTableWidget): Widget tableau associé.
        """
        selected_items = table_widget.selectedItems()
        if not selected_items:
            return  # Retourne si aucun élément n'est sélectionné

        # Récupère la valeur du temps t de la ligne sélectionnée
        selected_row = selected_items[0].row()
        t_value = float(table_widget.item(selected_row, 0).text())

        # Supprime la ligne existante, s'il y en a une
        if self.current_line is not None:
            self.current_line.remove()
        
        # Dessine une nouvelle ligne verticale pointillée
        self.current_line = sc.axes.axvline(t_value, color='g', linestyle='--', linewidth=1.5)
        sc.draw()  # Met à jour le dessin du graphique

    def onclick(self, event, solution, table_widget):
        """Gère les événements de clic sur le graphique.
        
        Args:
            event: Événement de clic.
            solution (OdeSolution): Solution du système d'équations.
            table_widget (QTableWidget): Widget tableau associé.
        """
        xdata = solution.t  # Récupère les données de temps
        # Récupère les données de Iion ou u selon la courbe cliquée
        #ydata = solution.y[0] if event.inaxes.get_legend_handles_labels()[1][0] == 'Iion(t)' else solution.y[1]
        # Calcule les distances entre le point cliqué et les points des données
        #distances = np.sqrt((xdata - event.xdata) ** 2 + (ydata - event.ydata) ** 2)
        distances = np.abs(xdata - event.xdata)
        ind = np.argmin(distances)  # Trouve l'indice du point le plus proche
        table_widget.selectRow(ind)  # Sélectionne la ligne correspondante dans le tableau
        table_widget.scrollToItem(table_widget.item(ind, 0), QTableWidget.PositionAtCenter)  # Fait défiler le tableau jusqu'à la ligne

if __name__ == "__main__":    
    # Initialisation des paramètres du modèle.
    params = Params()  # Crée une instance des paramètres
    tf = 200  # Temps final de simulation.
    
    # Création du système d'équations différentielles avec les paramètres.
    ode = Q_ODE(params)  # Crée une instance du système d'équations
    
    # Conditions initiales pour la simulation.
    u0 = [0.0, 0.0]  # Conditions initiales pour Iion et u
    
    # Définition de l'intervalle de temps pour la simulation.
    t_span = (0, tf)  # Intervalle de temps de 0 à tf
    
    # Temps d'évaluation pour la simulation.
    t_eval = np.linspace(t_span[0], t_span[1], 100000)  # Génère les temps d'évaluation
    
    # Dictionnaire pour stocker les solutions
    solutions = {}
    
    for method in methods:
        print(f'Résolution avec la méthode {method}')  # Affiche un message de résolution
        solutions[method] = solve_ivp(ode, t_span, u0, method=method, t_eval=t_eval)  # Résout le système

    # Détermination des bornes minimales et maximales pour les graphiques.
    t_min = min(solution.t.min() for solution in solutions.values())  # Temps minimal
    t_max = max(solution.t.max() for solution in solutions.values())  # Temps maximal
    y_min = min(solution.y.min() for solution in solutions.values())  # Valeur minimale des résultats
    y_max = max(solution.y.max() for solution in solutions.values())  # Valeur maximale des résultats
    
    app = QApplication(sys.argv)
    tab_widget = TabWidget()  # Crée une instance de TabWidget
    tab_widget.show()  # Affiche le widget d'onglets
    # Ajouter la fenêtre popup au démarrage
    # msg = QMessageBox()
    # msg.setIcon(QMessageBox.Information)
    # msg.setText("The Q integrator 2024")
    # msg.setWindowTitle("Welcome")
    # msg.setStandardButtons(QMessageBox.Ok)
    # msg.exec_()  # Affiche la fenêtre popup
    sys.exit(app.exec_())  # Exécute l'application Qt
