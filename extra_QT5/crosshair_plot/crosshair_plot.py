import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)

    def draw_viseur(self, x_data, y_data, position):
        self.axes.clear()
        self.axes.plot(x_data, y_data)
        self.axes.grid()
        
        if position is not None:
            x, y = position
            self.axes.axvline(x=x, color='red', linestyle='--')
            self.axes.axhline(y=y, color='red', linestyle='--')
            self.axes.plot(x, y, 'ro')
        
        self.draw()

class ViseurCarabine(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Viseur de Carabine avec Matplotlib')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout.addWidget(self.canvas)

        self.viseur_position = None

        self.x_data = np.linspace(-10, 10, 1000)
        self.y_data = np.sin(self.x_data)

        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_press_event", self.on_mouse_click)

        self.plot_function()

    def plot_function(self):
        self.canvas.draw_viseur(self.x_data, self.y_data, self.viseur_position)

    def on_mouse_move(self, event):
        if event.inaxes:
            mouse_x = event.xdata
            mouse_y = event.ydata

            # Trouver le point le plus proche sur la courbe
            distances = np.sqrt((self.x_data - mouse_x) ** 2 + (self.y_data - mouse_y) ** 2)
            min_index = np.argmin(distances)
            self.viseur_position = (self.x_data[min_index], self.y_data[min_index])
            self.plot_function()

    def on_mouse_click(self, event):
        if event.inaxes and self.viseur_position is not None:
            x, y = self.viseur_position
            print(f"Coordonnées du centre du viseur : ({x}, {y})")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = ViseurCarabine()
    fenetre.show()
    sys.exit(app.exec_())
