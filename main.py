import sys
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QMainWindow, 
    QPushButton, QCheckBox, QTextEdit, QScrollArea, QFrame, QGraphicsDropShadowEffect
)

# Import calculator functions and data from calculator.py
from calculator import ingredienti, find_optimal_combination

class SquareSlider(QWidget):
    """
    A discrete slider widget that displays a row of small squares.
    Users can select a minimum (low) and a maximum (high) index among the cells.

    The widget emits a valueChanged(low, high) signal when the selection changes.
    Modified to support values from 0 to 10 and reduced square dimensions.
    """
    valueChanged = Signal(int, int)  # Emits (low, high)

    def __init__(self, minimum=0, maximum=10, parent=None):
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self.num_cells = maximum - minimum + 1  # Supports 0 to 10 inclusive => 11 cells
        self._low = minimum
        self._high = maximum
        self._active_handle = None  # "low" or "high"
        self._cell_margin = 2
        self._cell_spacing = 2
        self._marker_radius = 4
        # Set the font to bold
        self._font = QFont("Arial", 7)
        self._font.setBold(True)
        self.setMinimumHeight(40)

    def minimum(self):
        return self._minimum

    def maximum(self):
        return self._maximum

    def low(self):
        return self._low

    def high(self):
        return self._high

    def setLow(self, value):
        if value < self._minimum:
            value = self._minimum
        if value > self._high:
            value = self._high
        if self._low != value:
            self._low = value
            self.valueChanged.emit(self._low, self._high)
            self.update()

    def setHigh(self, value):
        if value > self._maximum:
            value = self._maximum
        if value < self._low:
            value = self._low
        if self._high != value:
            self._high = value
            self.valueChanged.emit(self._low, self._high)
            self.update()

    def setLowHigh(self, low, high):
        if low < self._minimum:
            low = self._minimum
        if high > self._maximum:
            high = self._maximum
        if low > high:
            low, high = high, low
        self._low = low
        self._high = high
        self.valueChanged.emit(self._low, self._high)
        self.update()

    def cellRect(self, index):
        total_width = self.width() - 2 * self._cell_margin
        total_spacing = self._cell_spacing * (self.num_cells - 1)
        cell_width = (total_width - total_spacing) / self.num_cells
        cell_height = self.height() - 2 * self._cell_margin
        x = self._cell_margin + index * (cell_width + self._cell_spacing)
        y = self._cell_margin
        return QRect(int(x), int(y), int(cell_width), int(cell_height))

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

        low_rect = self.cellRect(self._low)
        high_rect = self.cellRect(self._high)
        low_center = low_rect.center()
        high_center = high_rect.center()
        painter.setBrush(QColor(80, 80, 230))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(low_center, self._marker_radius, self._marker_radius)
        painter.setBrush(QColor(230, 80, 80))
        painter.drawEllipse(high_center, self._marker_radius, self._marker_radius)

    def mousePressEvent(self, event):
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        low_center = self.cellRect(self._low).center()
        high_center = self.cellRect(self._high).center()
        dist_to_low = (pos - low_center).manhattanLength()
        dist_to_high = (pos - high_center).manhattanLength()
        if dist_to_low <= dist_to_high:
            self._active_handle = "low"
        else:
            self._active_handle = "high"
        self.updateHandleFromPosition(pos)

    def mouseMoveEvent(self, event):
        if self._active_handle is not None:
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            self.updateHandleFromPosition(pos)

    def mouseReleaseEvent(self, event):
        self._active_handle = None

    def updateHandleFromPosition(self, pos):
        for i in range(self.num_cells):
            rect = self.cellRect(i)
            if rect.contains(pos):
                if self._active_handle == "low":
                    self.setLow(i)
                elif self._active_handle == "high":
                    self.setHigh(i)
                break

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
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        main_layout.addWidget(header)

        # Ingredients selection using a grid layout (5 items per column).
        ingredients_frame = QFrame(self)
        ingredients_frame.setFrameShape(QFrame.StyledPanel)
        # Translucent dark background for the widget.
        ingredients_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 180, 180);
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
        # Title label for ingredients with a fixed background.
        ingredients_label = QLabel("Ingredienti obbligatori:", self)
        ingredients_label.setAlignment(Qt.AlignLeft)
        ingredients_label.setStyleSheet(
            "color: white; background-color: #4F4F4F; font-weight: bold; border-radius: 5px; padding: 2px;"
        )
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
            cb.setStyleSheet("color: white; font-weight: bold;")
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
            # Translucent dark background for the widget.
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
            # Title label for slider with a fixed background.
            title_label = QLabel(f"Range {param.capitalize()}:", self)
            title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            title_label.setStyleSheet(
                "color: white; background-color: #4F4F4F; font-weight: bold; border-radius: 5px; padding: 2px;"
            )
            title_layout.addWidget(title_label)
            range_label = QLabel("min 0 - max 10", self)
            range_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            range_label.setStyleSheet(
                "font-weight: bold; color: white; background-color: #4F4F4F; border-radius: 5px; padding: 2px;"
            )
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
                font-size: 16px;
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

        # Result text box now uses the same translucent background as the widgets.
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 30, 180);
                color: white;
                border-radius: 10px;
                padding: 8px;
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
    # Set a global bold font for the entire application.
    global_font = QFont("Arial", 10, QFont.Bold)
    app.setFont(global_font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())