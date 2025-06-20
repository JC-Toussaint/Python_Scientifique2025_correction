# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 20:39:56 2024

@author: toussaij
"""

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
from scipy.sparse.linalg import spsolve
import matplotlib.pyplot as plt
import time

import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMessageBox
)
#from matplotlib.backend_bases import MouseButton

from dialog_toolbox import PhysParamsDialog, SimParamsDialog  # Importer la classe depuis le module

class Phys:
    """
    Classe pour les paramètres physiques du problème.
    """
    def __init__(self, params):
        self.kth = params['kth']  # Conductivité thermique
        self.rho = params['rho']  # Masse volumique
        self.cp  = params['cp']    # Capacité calorifique
        self.type_cl_gauche = params['type_cl_gauche']  # Type de condition aux limites à gauche
        self.Tdg = params['Tdg']  # Température Dirichlet à gauche
        self.hg  = params['hg']    # Coefficient de transfert thermique à gauche (pour Neumann)
        self.Tag = params['Tag']  # Température extérieure à gauche (pour Neumann)
        self.type_cl_droite = params['type_cl_droite']  # Type de condition aux limites à droite
        self.Tdd = params['Tdd']  # Température Dirichlet à droite
        self.hd  = params['hd']    # Coefficient de transfert thermique à droite (pour Neumann)
        self.Tad = params['Tad']  # Température extérieure à droite (pour Neumann)

class Simul:
    """
    Classe pour les paramètres de simulation.
    """
    def __init__(self, params):
        self.longueur = params['longueur']  # Longueur
        self.dx = params['dx']              # Pas spatial
        self.dt = params['dt']              # Pas temporel
        self.tf = params['tf']              # Temps final
        self.NSF= params['NSF']             # Facteur d'échantillonnage (Sampling Factor) > 1
        self.theta = params['theta']        # Paramètre de la méthode de discrétisation
        self.Tinit = params['Tinit']        # Température initiale
        self.NP = round(self.longueur / self.dx + 1)  # Nombre de points du maillage
        self.dx = self.longueur / (self.NP-1) # Pas spatial corrigé
        self.NT = round(self.tf / self.dt + 1)  # Nombre de pas de temps dans [0, tf]
        self.dt = self.tf / (self.NT-1) # Pas de temps  corrigé
        
def build_A(phys, simul):
    """
    Construction de la matrice A du système d'équations linéaires

    Args:
        phys (Phys): Paramètres physiques.
        simul (Simul): Paramètres de simulation.

    Returns
    -------
        A (csr_matrix) : matrice de type 'compressed sparse row matrix'

    """
    NP = simul.NP
    dx = simul.dx
    dt = simul.dt
    theta = simul.theta

    # Paramètres physiques
    kth = phys.kth
    rho = phys.rho
    cp = phys.cp
    lambda_ = kth / (rho * cp)  # Conductivité thermique effective

    # Initialisation de la matrice creuse A
    A = lil_matrix((NP, NP), dtype=float)  # Row-based LIst of Lists sparse matrix
    
    if phys.type_cl_gauche == 'Dirichlet':
        # Condition de Dirichlet à gauche
        A[0, 0] = 1
    else:
        # Condition de Neumann à gauche
        hg = phys.hg
        A[0, 0] = 1.0 + 2.0 * lambda_ * theta * dt / (dx ** 2) + 2.0 * lambda_ * theta * dt / (dx ** 2) * dx * hg / kth
        A[0, 1] = -2.0 * lambda_ * theta * dt / (dx ** 2)

    # Conditions aux limites à droite
    if phys.type_cl_droite == 'Dirichlet':
        # Condition de Dirichlet à droite
        A[NP - 1, NP - 1] = 1
    else:
        # Condition de Neumann à droite
        hd = phys.hd
        A[NP - 1, NP - 1] = 1.0 + 2.0 * lambda_ * theta * dt / (dx ** 2) + 2.0 * lambda_ * theta * dt / (dx ** 2) * dx * hd / kth
        A[NP - 1, NP - 2] = -2.0 * lambda_ * theta * dt / (dx ** 2)

    # Points intérieurs du maillage
    for p in range(1, NP - 1):
        A[p, p - 1] = -lambda_ * theta * dt / (dx ** 2)
        A[p, p] = 1.0 + 2.0 * lambda_ * theta * dt / (dx ** 2)
        A[p, p + 1] = -lambda_ * theta * dt / (dx ** 2)
    return csr_matrix(A)
   
def build_RHS(Tprec, phys, simul): 
    """
    Construction du membre de droite du système d'équations linéaires

    Args:
        Tprec (numpy array) : températures aux noeuds de la grille
        phys (Phys): Paramètres physiques.
        simul (Simul): Paramètres de simulation.

    Returns
    -------
        b (numpy array) : valeurs aux noeuds de la grille
    """
    
    NP = simul.NP
    dx = simul.dx
    dt = simul.dt
    theta = simul.theta

    # Paramètres physiques
    kth = phys.kth
    rho = phys.rho
    cp = phys.cp
    lambda_ = kth / (rho * cp)  # Conductivité thermique effective
 
    # Initialisation du vecteur b
    b = np.zeros(NP)          # Vecteur du second membre
    
    if phys.type_cl_gauche == 'Dirichlet':
        # Condition de Dirichlet à gauche
        Tdg = phys.Tdg
        Tprec[0] = Tdg
        b[0] = 0
    else:
        # Condition de Neumann à gauche
        hg = phys.hg
        Tag = phys.Tag
        b[0] = -2.0 * lambda_ / (dx ** 2) * (Tprec[0] - Tprec[1] + dx * hg / kth * (Tprec[0] - Tag))

    # Conditions aux limites à droite
    if phys.type_cl_droite == 'Dirichlet':
        # Condition de Dirichlet à droite
        Tdd = phys.Tdd
        Tprec[NP - 1] = Tdd
        b[NP - 1] = 0
    else:
        # Condition de Neumann à droite
        hd = phys.hd
        Tad = phys.Tad
        b[NP - 1] = -2.0 * lambda_ / (dx ** 2) * (Tprec[NP - 1] - Tprec[NP - 2] + dx * hd / kth * (Tprec[NP - 1] - Tad))

    # Points intérieurs du maillage
    for p in range(1, NP - 1):
        b[p] = lambda_ * (Tprec[p + 1] + Tprec[p - 1] - 2 * Tprec[p]) / (dx ** 2)
            
    return b
        
class SimulationResult:
    def __init__(self, ts, x, Tn):
        self.ts = ts  # Temps d'échantillonnage
        self.x = x    # Positions des points du maillage
        self.Tn = np.asarray(Tn)  # Températures au fil du temps

    def plot(self):
        """
        Méthode pour tracer la solution.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Profils de température')
    
        for i in range(len(self.ts)):
            line, = ax.plot(self.x, self.Tn[i, :], label=f't={self.ts[i]:.2f}', linestyle='-', picker=True)
    
        annotation = None  # Variable to store the annotation object
        
        def onpick(event):
            nonlocal annotation  # Use the 'nonlocal' keyword to refer to the outer variable
        
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            points = tuple(zip(xdata[ind], ydata[ind]))
            print('onpick points:', points)
        
            # Remove the previous annotation if it exists
            if annotation:
                annotation.remove()
    
            # Add a new annotation with the coordinates of the clicked point
            annotation = ax.annotate(f'({points[0][0]:.3f}, {points[0][1]:.3f})',
                                     xy=points[0], xytext=(10, 10),
                                     textcoords='offset points',
                                     arrowprops=dict(arrowstyle='->'))
    
            fig.canvas.draw()  # Redraw the figure to update the annotation
     
        def onmotion(event):
            if event.inaxes == ax:
                # Change the cursor to a cross
                fig.canvas.set_cursor(3)  # 3 is the identifier for a cross cursor
        
        fig.canvas.mpl_connect('pick_event', onpick)
        fig.canvas.mpl_connect('motion_notify_event', onmotion)
        
        plt.xlabel('x [m]')
        plt.ylabel('T [K]')
        plt.grid(True)
        # Création de la légende
        legend = plt.legend()
        # Rendre la légende déplaçable
        legend.set_draggable(True)
        plt.show()  # Use plt.show() instead of fig.show()

        
def theta_schema(phys, simul):
    """
    Fonction pour résoudre l'équation de la chaleur en utilisant la méthode des différences finies implicite.
    
    Args:
        phys (Phys): Paramètres physiques.
        simul (Simul): Paramètres de simulation.
        
    Returns:
        SimulationResult: Résultats de la simulation encapsulés dans une classe.
    """
    # Extraction des paramètres
    dx = simul.dx
    dt = simul.dt
    tf = simul.tf
    NP = simul.NP  # Nombre de points du maillage
    NT = simul.NT  # Nombre de pas de temps dans [0, tf]
    NSF = simul.NSF # Facteur d'échantillonnage NSF>1 (Sampling Factor)
    
    # Initialisation des températures à t=0
    Tprec = np.zeros(NP)
    Tprec[:] = simul.Tinit

    v = np.zeros(NP)          # Vecteur de solution

    Tn = [Tprec.copy()] # liste pour stocker les profils de températures au fil du temps

    A = build_A(phys, simul)
    
    # Boucle sur le temps
    t = 0
    for nt in range(1, NT):
        
        # Construction du second membre rhs
        b = build_RHS(Tprec, phys, simul)

        # Résolution du système [A][v]=[b]
        v = spsolve(A, b)
        T = Tprec + dt * v  # création d'une nouvelle instance T de type numpy array
        t += dt
        
        # recopie des valeurs du tableau T dans Tprec sans créer une nouvelle instance Tprec
        Tprec[:] = T[:]

        # Stockage des températures du pas de temps courant
        if not(nt % NSF):
            Tn.append(T[:])
    # Fin de la boucle sur le temps

    x = np.arange(NP) * dx              # Positions des points du maillage
    ts = np.arange(len(Tn)) * (NSF * dt)  # instants d'échantillonnage de la solution 
    return SimulationResult(ts, x, Tn)

def dialog():
    """
    Saisie des paramètres de simulation

    Args:
        None

    Returns
    -------
        phys (Phys): Paramètres physiques.
        simul (Simul): Paramètres de simulation.        
    """
    dialog = PhysParamsDialog()
    if dialog.exec_() == QDialog.Accepted:
        params = dialog.get_values()
        print(params)
    # Création de l'instance phys            
    phys = Phys(params)

    dialog = SimParamsDialog()
    if dialog.exec_() == QDialog.Accepted:
        params = dialog.get_values()
        print(params)
    # Création de l'instance simul        
    simul = Simul(params)
    return phys, simul

if __name__ == "__main__":
    app = QApplication(sys.argv)
    

    phys, simul = dialog()
    
    # Début du chronométrage
    start_time = time.time()
    
    # Intégration de l'équation de la chaleur avec un theta-schéma
    result = theta_schema(phys, simul)

    # Fin du chronométrage
    end_time = time.time()
    
    # Calculer le temps écoulé
    elapsed_time = end_time - start_time
    
    print(f"Temps de résolution : {elapsed_time:.4f} secondes")
    
    # Dessine les différents profils aux instants de sauvegarde
    result.plot()
    
    #sys.exit(app.exec_())
