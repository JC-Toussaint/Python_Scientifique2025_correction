import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView, QSplitter, QMenu, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QGuiApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class DataApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data_frame = pd.DataFrame()

    def initUI(self):
        self.setWindowTitle('Data Visualization App')

        # Main layout
        main_layout = QHBoxLayout()

        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left layout for table and buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Load button
        load_button = QPushButton('Load Excel or CSV File')
        load_button.clicked.connect(self.load_file)
        left_layout.addWidget(load_button)

        # Plot button
        plot_button = QPushButton('Plot Data')
        plot_button.clicked.connect(self.plot_data)
        left_layout.addWidget(plot_button)

        # Table for displaying data
        self.table = QTableWidget()
        self.table.cellChanged.connect(self.update_dataframe)  # Connect the cellChanged signal
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.table.customContextMenuRequested.connect(self.show_cell_context_menu)
        left_layout.addWidget(self.table)

        # Set the table columns to stretch
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.sectionClicked.connect(self.select_column)

        splitter.addWidget(left_widget)

        # Right layout for plot
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)  # Connect the plot click event

        # Add the matplotlib toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)

        splitter.addWidget(right_widget)

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Connect the toolbar pan mode changes to custom cursor changes
        self.toolbar.pan()  # Initialize pan tool to set cursor change on pan activation
        self.toolbar._actions['pan'].triggered.connect(self.on_pan_mode)

    def load_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel or CSV File", "", "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    self.data_frame = pd.read_excel(file_path)
                elif file_path.endswith('.csv'):
                    # Trying with different separators
                    try:
                        self.data_frame = pd.read_csv(file_path)
                    except pd.errors.ParserError:
                        try:
                            self.data_frame = pd.read_csv(file_path, sep=';')
                        except pd.errors.ParserError:
                            self.data_frame = pd.read_csv(file_path, sep='\t')
                
                # Convert column names to strings if they are not
                self.data_frame.columns = self.data_frame.columns.map(str)
                self.update_table()
            except Exception as e:
                print(f"Error loading file: {e}")

    def update_table(self):
        self.table.blockSignals(True)  # Block signals to prevent recursive updates
        self.table.setRowCount(len(self.data_frame))
        self.table.setColumnCount(len(self.data_frame.columns))
        self.table.setHorizontalHeaderLabels(self.data_frame.columns)

        for i in range(len(self.data_frame)):
            for j in range(len(self.data_frame.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(self.data_frame.iat[i, j])))

        self.table.blockSignals(False)  # Unblock signals after the update

    def update_dataframe(self, row, column):
        value = self.table.item(row, column).text()
        self.data_frame.iat[row, column] = value

    def select_column(self, index):
        self.table.blockSignals(True)
        self.table.clearSelection()
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        for row in range(self.table.rowCount()):
            self.table.item(row, index).setSelected(True)
        self.table.blockSignals(False)
        
        # Show context menu for copying and pasting
        self.show_context_menu(index)

    def show_context_menu(self, index):
        menu = QMenu(self)
        copy_action = menu.addAction("Copy Column")
        copy_action.triggered.connect(lambda: self.copy_column(index))
        paste_action = menu.addAction("Paste Column")
        paste_action.triggered.connect(lambda: self.paste_column(index))
        delete_action = menu.addAction("Delete Column")
        delete_action.triggered.connect(lambda: self.delete_column(index))
        menu.exec_(QCursor.pos())

    def copy_column(self, index):
        column_data = []
        for row in range(self.table.rowCount()):
            column_data.append(self.table.item(row, index).text())
        column_str = '\n'.join(column_data)
        QGuiApplication.clipboard().setText(column_str)

    def paste_column(self, index):
        clipboard = QGuiApplication.clipboard()
        column_data = clipboard.text().split('\n')
        if len(column_data) != self.table.rowCount():
            print("The number of rows in the clipboard does not match the table.")
            return
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            self.table.setItem(row, index, QTableWidgetItem(column_data[row]))
        self.table.blockSignals(False)
        self.update_dataframe_from_table(index)

    def delete_column(self, index):
        self.table.removeColumn(index)
        self.data_frame.drop(columns=[self.data_frame.columns[index]], inplace=True)

    def update_dataframe_from_table(self, column_index):
        for row in range(self.table.rowCount()):
            value = self.table.item(row, column_index).text()
            self.data_frame.iat[row, column_index] = value

    def plot_data(self):
        if not self.data_frame.empty:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            x_data = pd.to_numeric(self.data_frame.iloc[:, 0])  # Première colonne pour l'axe des x
            for col in self.data_frame.columns[1:]:  # Tracer toutes les autres colonnes par rapport à la première
                y_data = pd.to_numeric(self.data_frame[col])
                ax.plot(x_data, y_data, marker='o', linestyle='-', label=col)
            
            ax.set_xlabel(self.data_frame.columns[0])
            ax.set_ylabel('Values')
            ax.set_title('Data Visualization')
            ax.legend()
            ax.grid()
            self.canvas.draw()

    def on_plot_click(self, event):
        if event.inaxes:
            x_click = event.xdata
            y_click = event.ydata

            # Find the closest point
            x_data = pd.to_numeric(self.data_frame.iloc[:, 0])
            y_columns = self.data_frame.columns[1:]
            distances = []
            for col in y_columns:
                y_data = pd.to_numeric(self.data_frame[col])
                distances.append(((x_data - x_click)**2 + (y_data - y_click)**2)**0.5)
            
            distances = pd.DataFrame(distances).T
            closest_indices = distances.sum(axis=1).idxmin()

            # Highlight the corresponding row in the table
            self.table.blockSignals(True)
            self.table.selectRow(closest_indices)
            self.table.blockSignals(False)

    def on_pan_mode(self):
        if self.toolbar._active == 'PAN':
            QApplication.setOverrideCursor(Qt.CrossCursor)
        else:
            QApplication.restoreOverrideCursor()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DataApp()
    ex.show()
    sys.exit(app.exec_())
