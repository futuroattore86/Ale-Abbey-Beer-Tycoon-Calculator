import sys
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QThread, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QIcon, QFontDatabase
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QMainWindow, 
    QPushButton, QCheckBox, QTextEdit, QScrollArea, QFrame, QGraphicsDropShadowEffect
)
from math import cos, sin, pi

# Import calculator functions and data from calculator.py
from calculator import ingredienti, find_optimal_combination

class SpinningLoader(QWidget):
    def __init__(self, parent=None, size=32, color=QColor(74, 158, 255)):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.angle = 0
        self.color = color
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.dots = 8  # Numero di punti nel cerchio
        self.stopped = True

    def rotate(self):
        self.angle = (self.angle + 45) % 360
        self.update()

    def start(self):
        if self.stopped:
            self.stopped = False
            self.timer.start(100)  # Aggiorna ogni 100ms

    def stop(self):
        self.stopped = True
        self.timer.stop()

    def paintEvent(self, event):
        if self.stopped:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 3
        
        for i in range(self.dots):
            angle = i * (360 / self.dots) + self.angle
            rad_angle = angle * pi / 180
            x = center.x() + radius * cos(rad_angle)
            y = center.y() + radius * sin(rad_angle)
            
            opacity = (i / self.dots) * 255
            dot_color = QColor(self.color)
            dot_color.setAlpha(int(opacity))
            
            painter.setBrush(dot_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(int(x), int(y)), 3, 3)

class CalculationWorker(QThread):
    finished = Signal(tuple)
    
    def __init__(self, required_ingredients, ranges):
        super().__init__()
        self.required_ingredients = required_ingredients
        self.ranges = ranges
        
    def run(self):
        result = find_optimal_combination(self.required_ingredients, self.ranges)
        self.finished.emit(result)

class SquareSlider(QWidget):
    valueChanged = Signal(int, int)

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
        self._font = QFont("Alegreya", 11)
        self._font.setBold(True)
        self.setMinimumHeight(45)
        self.setMouseTracking(True)

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
            if self._low <= i <= self._high:
                painter.setBrush(QColor(100, 150, 250))
            else:
                painter.setBrush(QColor(200, 200, 200))
            
            if self._selection_start is not None and i == self._current_cell:
                painter.setBrush(QColor(150, 200, 250))

            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(rect)
            
            text = f"{i}"
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()
            text_x = rect.x() + (rect.width() - text_width) / 2
            text_y = rect.y() + (rect.height() + text_height) / 2 - 3
            painter.setPen(QColor("black"))
            painter.drawText(int(text_x), int(text_y), text)

    def mousePressEvent(self, event):
        cell = self.getCellAtPosition(event.position().toPoint())
        if cell is not None:
            self._selection_start = cell
            self._current_cell = cell
            self._low = cell
            self._high = cell
            self.valueChanged.emit(self._low, self._high)
            self.update()

    def mouseMoveEvent(self, event):
        if self._selection_start is not None:
            cell = self.getCellAtPosition(event.position().toPoint())
            if cell is not None and cell != self._current_cell:
                self._current_cell = cell
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
        self.setWindowTitle("Ale Abbey Monastery Brewery Tycoon Calculator")
        self.resize(800, 900)

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

        header = QLabel("Ale Abbey Monastery Brewery Tycoon Calculator", self)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 28px;
            font-family: Alegreya;
            font-weight: bold;
            color: white;
        """)
        main_layout.addWidget(header)

        ingredients_frame = QFrame(self)
        ingredients_frame.setFrameShape(QFrame.StyledPanel)
        ingredients_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 10px;
            }
            QLabel {
                background: none;
                background-color: transparent;
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
            font-family: Alegreya;
            font-size: 14px;
            font-weight: bold;
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
                QLabel {
                    background: none;
                    background-color: transparent;
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
                font-family: Alegreya;
                font-size: 14px;
                font-weight: bold;
                padding: 2px;
            """)
            title_layout.addWidget(title_label)
            range_label = QLabel("min 0 - max 10", self)
            range_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            range_label.setStyleSheet("""
                color: white;
                font-family: Alegreya;
                font-size: 14px;
                font-weight: bold;
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
            QPushButton:disabled {
                background-color: rgba(30, 30, 30, 100);
                color: rgba(255, 255, 255, 128);
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

        self.loading_widget = QWidget(self.result_text)
        loading_layout = QHBoxLayout(self.loading_widget)
        loading_layout.setContentsMargins(10, 10, 10, 10)
        loading_layout.setSpacing(10)
        
        self.spinner = SpinningLoader(self, size=24)
        loading_layout.addWidget(self.spinner)
        
        self.loading_label = QLabel("Ricerca in corso...\nAttendi mentre calcolo la combinazione ottimale...", self)
        self.loading_label.setStyleSheet("""
            color: white;
            font-family: Alegreya;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
        """)
        loading_layout.addWidget(self.loading_label)
        loading_layout.addStretch()
        
        self.loading_widget.hide()
        main_layout.addWidget(self.result_text)

    def updateParameterLabel(self, param, low, high):
        label = self.param_labels.get(param)
        if label:
            label.setText(f"min {low} - max {high}")

    def compute_combination(self):
        self.compute_button.setEnabled(False)
        self.result_text.clear()
        self.loading_widget.show()
        self.spinner.start()
        
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

        self.worker = CalculationWorker(required_ingredients, ranges)
        self.worker.finished.connect(self.on_calculation_complete)
        self.worker.start()

    def on_calculation_complete(self, result):
        self.spinner.stop()
        self.loading_widget.hide()
        
        quantities, values, counter = result
        
        if quantities:
            result_text = "✅ Combinazione ottimale trovata!\n\n"
            result_text += "Ingredienti da utilizzare:\n"
            result_text += "-" * 30 + "\n"
            for ingr, qty in zip(ingredienti, quantities):
                if qty > 0:
                    result_text += f"{ingr}: {qty} unità\n"
            
            result_text += "\nValori ottenuti:\n"
            result_text += "-" * 30 + "\n"
            for key, val in values.items():
                result_text += f"{key.capitalize()}: {val:.1f}\n"
            
            result_text += f"\nCombinazioni esaminate: {counter:,}\n"
        else:
            result_text = "❌ Nessuna combinazione valida trovata!\n\n"
            result_text += "Possibili cause:\n"
            result_text += "-" * 30 + "\n"
            result_text += "• Range dei valori troppo restrittivo\n"
            result_text += "• Troppi ingredienti obbligatori selezionati\n"
            result_text += "• Combinazione di requisiti impossibile da soddisfare\n\n"
            
            if self.worker.required_ingredients:
                result_text += "Ingredienti obbligatori selezionati:\n"
                result_text += "-" * 30 + "\n"
                for idx in self.worker.required_ingredients:
                    result_text += f"• {ingredienti[idx]}\n"
            
            result_text += "\nRange richiesti:\n"
            result_text += "-" * 30 + "\n"
            for param in self.parameters:
                low, high = self.worker.ranges[param]
                result_text += f"• {param.capitalize()}: {low} - {high}\n"
            
            result_text += f"\nCombinazioni esaminate: {counter:,}\n"

        self.result_text.setPlainText(result_text)
        self.compute_button.setEnabled(True)
        self.worker.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font_id = QFontDatabase.addApplicationFont("fonts/Alegreya-Regular.ttf")
    font_id_bold = QFontDatabase.addApplicationFont("fonts/Alegreya-Bold.ttf")
    
    if font_id == -1 or font_id_bold == -1:
        print("Warning: Could not load Alegreya font. Falling back to system font.")
    
    global_font = QFont("Alegreya", 12)
    global_font.setBold(True)
    app.setFont(global_font)
    
    app.setStyleSheet("""
        * {
            font-family: Alegreya;
            font-weight: bold;
        }
        QLabel {
            background: none;
            background-color: transparent;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
