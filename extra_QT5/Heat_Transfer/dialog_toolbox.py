# dialog_toolbox.py

from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QLabel, QComboBox, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont

class PhysParamsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phys")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        d = {'kth': '1.65', 'rho': '2150.0', 'cp': '1000.0', 
             'type_cl_gauche': 'A definir', 'Tdg': '300', 'hg': '10', 'Tag': '300', 
             'type_cl_droite': 'A definir', 'Tdd': '300', 'hd': '10', 'Tad': '300'}
        
        # Appliquer la police Arial, taille 12
        font = QFont("Arial", 12)
        self.setFont(font)

        layout = QFormLayout()

        # Paramètres physiques avec valeurs par défaut
        self.kth_edit = QLineEdit(d['kth'])
        self.kth_edit.setFont(font)
        self.rho_edit = QLineEdit(d['rho'])
        self.rho_edit.setFont(font)
        self.cp_edit = QLineEdit(d['cp'])
        self.cp_edit.setFont(font)

        # Utiliser QLabel pour le texte avec LaTeX
        kth_label = QLabel("k<sub>th</sub> [W][m<sup>-1</sup>][K<sup>-1</sup>]:")
        kth_label.setFont(font)
        rho_label = QLabel("ρ [kg][m<sup>-3</sup>]:")
        rho_label.setFont(font)
        cp_label = QLabel("c<sub>p</sub> [J][kg<sup>-1</sup>][m<sup>-3</sup>]:")
        cp_label.setFont(font)

        layout.addRow(kth_label, self.kth_edit)
        layout.addRow(rho_label, self.rho_edit)
        layout.addRow(cp_label, self.cp_edit)

        # Ajouter un espace vide pour le saut de ligne
        layout.addRow(QLabel())  # Ligne vide

        # Conditions aux limites à gauche
        self.type_cl_gauche_combo = QComboBox()
        self.type_cl_gauche_combo.addItems(["A definir", "Dirichlet", "Neumann"])
        self.type_cl_gauche_combo.setFont(font)
        self.type_cl_gauche_combo.currentIndexChanged.connect(self.update_left_side_fields)

        # Valeurs par défaut
        self.Tdg_edit = QLineEdit(d['Tdg'])
        self.Tdg_edit.setFont(font)
        self.hg_edit = QLineEdit(d['hg'])
        self.hg_edit.setFont(font)
        self.Tag_edit = QLineEdit(d['Tag'])
        self.Tag_edit.setFont(font)

        layout.addRow("Conditions aux limites à gauche :", self.type_cl_gauche_combo)
        layout.addRow("T<sub>dg</sub> [K]:", self.Tdg_edit)
        layout.addRow("h<sub>g</sub> [W][m<sup>-2</sup>][K<sup>-1</sup>]:", self.hg_edit)
        layout.addRow("T<sub>ag</sub> [K]:", self.Tag_edit)

        self.Tdg_edit.setDisabled(True)
        self.hg_edit.setDisabled(True)
        self.Tag_edit.setDisabled(True)

        # Ajouter un espace vide pour le saut de ligne
        layout.addRow(QLabel())  # Ligne vide

        # Conditions aux limites à droite
        self.type_cl_droite_combo = QComboBox()
        self.type_cl_droite_combo.addItems(["A definir", "Dirichlet", "Neumann"])
        self.type_cl_droite_combo.setFont(font)
        self.type_cl_droite_combo.currentIndexChanged.connect(self.update_right_side_fields)

        # Valeurs par défaut
        self.Tdd_edit = QLineEdit(d['Tdd'])
        self.Tdd_edit.setFont(font)
        self.hd_edit = QLineEdit(d['hd'])
        self.hd_edit.setFont(font)
        self.Tad_edit = QLineEdit(d['Tad'])
        self.Tad_edit.setFont(font)

        layout.addRow("Conditions aux limites à droite :", self.type_cl_droite_combo)
        layout.addRow("T<sub>dd</sub> [K]:", self.Tdd_edit)
        layout.addRow("h<sub>d</sub> [W][m<sup>-2</sup>][K<sup>-1</sup>]:", self.hd_edit)
        layout.addRow("T<sub>ad</sub> [K]:", self.Tad_edit)

        self.Tdd_edit.setDisabled(True)
        self.hd_edit.setDisabled(True)
        self.Tad_edit.setDisabled(True)

        # Boutons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.setFont(font)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(font)
        self.ok_button.clicked.connect(self.check_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Ajouter un espace vide avant les boutons
        layout.addRow(QLabel())  # Ligne vide
        layout.addRow(button_layout)

        self.setLayout(layout)

    def update_left_side_fields(self):
        if self.type_cl_gauche_combo.currentText() == "Dirichlet":
            self.Tdg_edit.setEnabled(True)
            self.hg_edit.setDisabled(True)
            self.Tag_edit.setDisabled(True)
        else:
            self.Tdg_edit.setDisabled(True)
            self.hg_edit.setEnabled(True)
            self.Tag_edit.setEnabled(True)

    def update_right_side_fields(self):
        if self.type_cl_droite_combo.currentText() == "Dirichlet":
            self.Tdd_edit.setEnabled(True)
            self.hd_edit.setDisabled(True)
            self.Tad_edit.setDisabled(True)
        else:
            self.Tdd_edit.setDisabled(True)
            self.hd_edit.setEnabled(True)
            self.Tad_edit.setEnabled(True)

    def check_and_accept(self):
        if self.type_cl_gauche_combo.currentText() == "A definir" or self.type_cl_droite_combo.currentText() == "A definir":
            QMessageBox.warning(self, "Validation Error", "Vous devez définir les deux conditions aux limites avant de continuer.")
        else:
            self.accept()

    def get_values(self):
        values = {
            'kth': float(self.kth_edit.text()),
            'rho': float(self.rho_edit.text()),
            'cp': float(self.cp_edit.text()),
            'type_cl_gauche': self.type_cl_gauche_combo.currentText(),
            'Tdg': float(self.Tdg_edit.text()) if self.Tdg_edit.isEnabled() else None,
            'hg': float(self.hg_edit.text()) if self.hg_edit.isEnabled() else None,
            'Tag': float(self.Tag_edit.text()) if self.Tag_edit.isEnabled() else None,
            'type_cl_droite': self.type_cl_droite_combo.currentText(),
            'Tdd': float(self.Tdd_edit.text()) if self.Tdd_edit.isEnabled() else None,
            'hd': float(self.hd_edit.text()) if self.hd_edit.isEnabled() else None,
            'Tad': float(self.Tad_edit.text()) if self.Tad_edit.isEnabled() else None
        }
        return values

class SimParamsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paramètres Physiques")
        self.setGeometry(100, 100, 400, 350)  # Ajusté la taille pour accommoder le nouveau champ
        self.init_ui()

    def init_ui(self):
        # Valeurs par défaut
        d = {
            'longueur': '1.0', 
            'dx': '0.02', 
            'dt': '100', 
            'tf': '100000.0', 
            'NSF': '100',  # Valeur par défaut pour NSF (sampling factor)
            'theta': '0.5', 
            'Tinit': '500.0'
        }

        # Appliquer la police Arial, taille 12
        font = QFont("Arial", 12)
        self.setFont(font)

        layout = QFormLayout()

        # Champs pour les paramètres avec valeurs par défaut
        self.longueur_edit = QLineEdit(d['longueur'])
        self.longueur_edit.setFont(font)
        self.dx_edit = QLineEdit(d['dx'])
        self.dx_edit.setFont(font)
        self.dt_edit = QLineEdit(d['dt'])
        self.dt_edit.setFont(font)
        self.tf_edit = QLineEdit(d['tf'])
        self.tf_edit.setFont(font)
        self.NSF_edit = QLineEdit(d['NSF'])
        self.NSF_edit.setFont(font)
        self.theta_edit = QLineEdit(d['theta'])
        self.theta_edit.setFont(font)
        self.Tinit_edit = QLineEdit(d['Tinit'])
        self.Tinit_edit.setFont(font)

        # Libellés pour les champs
        longueur_label = QLabel("Longueur [m]:")
        longueur_label.setFont(font)
        dx_label = QLabel("dx [m]:")
        dx_label.setFont(font)
        dt_label = QLabel("dt [s]:")
        dt_label.setFont(font)
        tf_label = QLabel("tf [s]:")
        tf_label.setFont(font)
        NSF_label = QLabel("NSF (Entier > 1):")
        NSF_label.setFont(font)
        theta_label = QLabel("Theta:")
        theta_label.setFont(font)
        Tinit_label = QLabel("Température initiale [K]:")
        Tinit_label.setFont(font)

        # Ajouter les lignes au formulaire
        layout.addRow(longueur_label, self.longueur_edit)
        layout.addRow(dx_label, self.dx_edit)
        layout.addRow(dt_label, self.dt_edit)
        layout.addRow(tf_label, self.tf_edit)
        layout.addRow(NSF_label, self.NSF_edit)
        layout.addRow(theta_label, self.theta_edit)
        layout.addRow(Tinit_label, self.Tinit_edit)

        # Ajouter un espace vide avant les boutons
        layout.addRow(QLabel())  # Ligne vide

        # Boutons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.setFont(font)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(font)
        self.ok_button.clicked.connect(self.check_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Ajouter les boutons au formulaire
        layout.addRow(button_layout)

        self.setLayout(layout)

    def check_and_accept(self):
        try:
            # Vérifier que tous les champs sont remplis et sont des nombres
            float(self.longueur_edit.text())
            float(self.dx_edit.text())
            float(self.dt_edit.text())
            float(self.tf_edit.text())
            int_NSF = int(self.NSF_edit.text())
            if int_NSF <= 1:
                raise ValueError("NSF doit être un entier supérieur à 1.")
            float(self.theta_edit.text())
            float(self.Tinit_edit.text())
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", f"Erreur de validation: {e}")

    def get_values(self):
        values = {
            'longueur': float(self.longueur_edit.text()),
            'dx': float(self.dx_edit.text()),
            'dt': float(self.dt_edit.text()),
            'tf': float(self.tf_edit.text()),
            'NSF': int(self.NSF_edit.text()),
            'theta': float(self.theta_edit.text()),
            'Tinit': float(self.Tinit_edit.text())
        }
        return values

