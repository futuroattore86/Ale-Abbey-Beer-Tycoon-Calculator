import sys
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QIcon, QFontDatabase
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QMainWindow, 
    QPushButton, QCheckBox, QTextEdit, QScrollArea, QFrame, QGraphicsDropShadowEffect
)

# Import calculator functions and data from calculator.py
from calculator import ingredienti, find_optimal_combination

class SquareSlider(QWidget):
    valueChanged = Signal(int, int)  # Emits (low, high)

    def __init__(self, minimum=0, maximum=10, parent=None):
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self.num_cells = maximum - minimum + 1
        self._low = minimum
        self._high = maximum
        self._cell_margin = 2
        self._cell_spacing = 2
        self._selection_start = None
        self._current_cell = None
        # Set the font to Alegreya bold with increased size
        self._font = QFont("Alegreya", 9)
        self._font.setBold(True)
        self.setMinimumHeight(40)
        self.setMouseTracking(True)  # Abilita il tracking del mouse

    def cellRect(self, index):
        total_width = self.width() - 2 * self._cell_margin
        total_spacing = self._cell_spacing * (self.num_cells - 1)
        cell_width = (total_width - total_spacing) / self.num_cells
        cell_height = self.height() - 2 * self._cell_margin
        x = self._cell_margin + index * (cell_width + self._cell_spacing)
        y = self._cell_margin
        return QRect(int(x), int(y), int(cell_width), int(cell_height))

    def getCellAtPosition(self, pos):
        for i in range(self.num_cells):
            if self.cellRect(i).contains(pos):
                return i
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self._font)

        for i in range(self.num_cells):
            rect = self.cellRect(i)
            # Colora le celle nel range selezionato
            if self._low <= i <= self._high:
                painter.setBrush(QColor(100, 150, 250))
            else:
                painter.setBrush(QColor(200, 200, 200))
            
            # Evidenzia la cella su cui si trova il mouse durante la selezione
            if self._selection_start is not None and i == self._current_cell:
                painter.setBrush(QColor(150, 200, 250))

            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(rect)
            
            # Disegna il numero
            text = f"{i}"
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()
            text_x = rect.x() + (rect.width() - text_width) / 2
            text_y = rect.y() + (rect.height() + text_height) / 2 - 3
            painter.setPen(QColor("black"))
            painter.drawText(int(text_x), int(text_y), text)

    def mousePressEvent(self, event):
        cell = self.getCellAtPosition(event.pos())
        if cell is not None:
            self._selection_start = cell
            self._current_cell = cell
            self._low = cell
            self._high = cell
            self.valueChanged.emit(self._low, self._high)
            self.update()

    def mouseMoveEvent(self, event):
        if self._selection_start is not None:
            cell = self.getCellAtPosition(event.pos())
            if cell is not None and cell != self._current_cell:
                self._current_cell = cell
                # Aggiorna il range in base alla direzione della selezione
                if cell < self._selection_start:
                    self._low = cell
                    self._high = self._selection_start
                else:
                    self._low = self._selection_start
                    self._high = cell
                self.valueChanged.emit(self._low, self._high)
                self.update()

    def mouseReleaseEvent(self, event):
        if self._selection_start is not None:
            self._selection_start = None
            self._current_cell = None
            self.update()

    def minimum(self):
        return self._minimum

    def maximum(self):
        return self._maximum

    def low(self):
        return self._low

    def high(self):
        return self._high

    def setLow(self, value):
        if self._minimum <= value <= self._high:
            self._low = value
            self.valueChanged.emit(self._low, self._high)
            self.update()

    def setHigh(self, value):
        if self._low <= value <= self._maximum:
            self._high = value
            self.valueChanged.emit(self._low, self._high)
            self.update()

    def setLowHigh(self, low, high):
        if low > high:
            low, high = high, low
        if self._minimum <= low and high <= self._maximum:
            self._low = low
            self._high = high
            self.valueChanged.emit(self._low, self._high)
            self.update()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ale-Abbey Beer Tycoon Calculator")
        self.resize(800, 900)

        # Setup background using background.jpg.
        self.setStyleSheet("""
            QMainWindow {
                background-image: url(background.jpg);
                background-repeat: no-repeat;
                background-position: center;
            }
        """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        header = QLabel("Ale-Abbey Beer Tycoon Calculator", self)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 28px;
            font-family: Alegreya;
            font-weight: bold;
            color: white;
        """)
        main_layout.addWidget(header)

        # Ingredients selection using a grid layout (5 items per column).
        ingredients_frame = QFrame(self)
        ingredients_frame.setFrameShape(QFrame.StyledPanel)
        ingredients_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 10px;
            }
        """)
        ingredients_shadow = QGraphicsDropShadowEffect()
        ingredients_shadow.setBlurRadius(15)
        ingredients_shadow.setXOffset(3)
        ingredients_shadow.setYOffset(3)
        ingredients_shadow.setColor(QColor(0, 0, 0, 160))
        ingredients_frame.setGraphicsEffect(ingredients_shadow)

        ingredients_layout = QVBoxLayout(ingredients_frame)
        ingredients_label = QLabel("Ingredienti obbligatori:", self)
        ingredients_label.setAlignment(Qt.AlignLeft)
        ingredients_label.setStyleSheet("""
            color: white;
            background-color: #4F4F4F;
            font-family: Alegreya;
            font-size: 14px;
            font-weight: bold;
            border-radius: 5px;
            padding: 2px;
        """)
        ingredients_layout.addWidget(ingredients_label)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(150)
        ing_widget = QWidget(self)
        grid_layout = QGridLayout(ing_widget)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setVerticalSpacing(5)
        for index, ingr in enumerate(ingredienti):
            cb = QCheckBox(ingr, self)
            cb.setStyleSheet("""
                color: white;
                font-family: Alegreya;
                font-size: 12px;
                font-weight: bold;
            """)
            row = index % 5
            col = index // 5
            grid_layout.addWidget(cb, row, col)
        ing_widget.setLayout(grid_layout)
        scroll_area.setWidget(ing_widget)
        ingredients_layout.addWidget(scroll_area)
        main_layout.addWidget(ingredients_frame)

        # Parameters selection using SquareSlider.
        self.parameters = ["gusto", "colore", "gradazione", "schiuma"]
        self.sliders = {}
        self.param_labels = {}
        for param in self.parameters:
            param_frame = QFrame(self)
            param_frame.setFrameShape(QFrame.StyledPanel)
            param_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 30, 30, 180);
                    border-radius: 10px;
                }
            """)
            param_shadow = QGraphicsDropShadowEffect()
            param_shadow.setBlurRadius(15)
            param_shadow.setXOffset(3)
            param_shadow.setYOffset(3)
            param_shadow.setColor(QColor(0, 0, 0, 160))
            param_frame.setGraphicsEffect(param_shadow)

            param_layout = QVBoxLayout(param_frame)
            title_layout = QHBoxLayout()
            title_label = QLabel(f"Range {param.capitalize()}:", self)
            title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            title_label.setStyleSheet("""
                color: white;
                background-color: #4F4F4F;
                font-family: Alegreya;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 2px;
            """)
            title_layout.addWidget(title_label)
            range_label = QLabel("min 0 - max 10", self)
            range_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            range_label.setStyleSheet("""
                color: white;
                background-color: #4F4F4F;
                font-family: Alegreya;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 2px;
            """)
            title_layout.addWidget(range_label)
            self.param_labels[param] = range_label
            param_layout.addLayout(title_layout)

            slider = SquareSlider(0, 10, self)
            slider.valueChanged.connect(lambda low, high, p=param: self.updateParameterLabel(p, low, high))
            param_layout.addWidget(slider)
            self.sliders[param] = slider
            main_layout.addWidget(param_frame)

        # Compute button with integrated search icon.
        self.compute_button = QPushButton("Trova Ricetta", self)
        icon = QIcon("search_icon.png")
        self.compute_button.setIcon(icon)
        self.compute_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-family: Alegreya;
                padding: 8px;
                background-color: rgba(30, 30, 30, 180);
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 200);
            }
        """)
        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setBlurRadius(15)
        button_shadow.setXOffset(3)
        button_shadow.setYOffset(3)
        button_shadow.setColor(QColor(0, 0, 0, 160))
        self.compute_button.setGraphicsEffect(button_shadow)
        self.compute_button.clicked.connect(self.compute_combination)
        main_layout.addWidget(self.compute_button)

        # Result text box
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 30, 180);
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-family: Alegreya;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        result_shadow = QGraphicsDropShadowEffect()
        result_shadow.setBlurRadius(15)
        result_shadow.setXOffset(3)
        result_shadow.setYOffset(3)
        result_shadow.setColor(QColor(0, 0, 0, 160))
        self.result_text.setGraphicsEffect(result_shadow)
        main_layout.addWidget(self.result_text)

    def updateParameterLabel(self, param, low, high):
        label = self.param_labels.get(param)
        if label:
            label.setText(f"min {low} - max {high}")
        print(f"{param.capitalize()} updated: {low} - {high}")

    def compute_combination(self):
        required_ingredients = []
        scroll_area = self.findChild(QScrollArea)
        if scroll_area:
            widget = scroll_area.widget()
            if widget:
                checkboxes = widget.findChildren(QCheckBox)
                for i, cb in enumerate(checkboxes):
                    if cb.isChecked():
                        required_ingredients.append(i)

        ranges = {}
        for param in self.parameters:
            slider = self.sliders[param]
            ranges[param] = (slider.low(), slider.high())
        quantities, values, counter = find_optimal_combination(required_ingredients, ranges)
        if quantities:
            result = "Optimal Combination Found:\n\n"
            for ingr, qty in zip(ingredienti, quantities):
                result += f"{ingr}: {qty} units\n"
            result += "\nCalculated Values:\n"
            for key, val in values.items():
                result += f"{key.capitalize()}: {val}\n"
            result += f"\nCombinations Examined: {counter}\n"
        else:
            result = f"No valid combination found.\nCombinations Examined: {counter}\n"
        self.result_text.setPlainText(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load Alegreya font
    font_id = QFontDatabase.addApplicationFont("fonts/Alegreya-Regular.ttf")
    font_id_bold = QFontDatabase.addApplicationFont("fonts/Alegreya-Bold.ttf")
    
    if font_id == -1 or font_id_bold == -1:
        print("Warning: Could not load Alegreya font. Falling back to system font.")
    
    # Set global bold font for the entire application
    global_font = QFont("Alegreya", 12)
    global_font.setBold(True)
    app.setFont(global_font)
    
    # Set global style for the application
    app.setStyleSheet("""
        * {
            font-family: Alegreya;
            font-weight: bold;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
