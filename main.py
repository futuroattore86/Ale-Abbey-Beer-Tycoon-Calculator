import sys
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QThread, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QIcon, QFontDatabase, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QMainWindow, 
    QPushButton, QCheckBox, QTextEdit, QScrollArea, QFrame, QGraphicsDropShadowEffect
)
from math import cos, sin, pi

# Import calculator functions and data from calculator.py
from calculator import ingredienti, INGREDIENTI_ORDINE_SBLOCCO, UNLOCKABLE_INGREDIENTS, find_optimal_combination, ALWAYS_AVAILABLE

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
    
    def __init__(self, required_ingredients, ranges, unlocked_ingredients):
        super().__init__()
        self.required_ingredients = required_ingredients
        self.ranges = ranges
        self.unlocked_ingredients = unlocked_ingredients
        
    def run(self):
        result = find_optimal_combination(self.required_ingredients, self.ranges, self.unlocked_ingredients)
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
class OutlinedLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.outline_color = QColor("#000000")  # Colore del contorno (nero)
        self.text_color = QColor("#FFD700")     # Colore del testo (oro)
        self.outline_thickness = 3               # Spessore del contorno
        self.setContentsMargins(10, 5, 10, 5)
        
    def setOutlineColor(self, color):
        self.outline_color = QColor(color)
        self.update()
        
    def setTextColor(self, color):
        self.text_color = QColor(color)
        self.update()
        
    def setOutlineThickness(self, thickness):
        self.outline_thickness = thickness
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self.outline_color)
        pen.setWidth(self.outline_thickness)
        painter.setPen(pen)
        
        margins = self.contentsMargins()
        
        path = QPainterPath()
        metrics = painter.fontMetrics()
        descent = metrics.descent()
        
        textHeight = metrics.height()
        y = (self.height() + textHeight - descent) / 2
        path.addText(0, y, self.font(), self.text())
        
        # Centra il testo nel widget
        bounds = path.boundingRect()
        xOffset = (self.width() - margins.left() - margins.right() - bounds.width()) / 2
        yOffset = -bounds.y() / 2
        
        painter.translate(xOffset, yOffset)
        
        painter.strokePath(path, pen)
        painter.setPen(self.text_color)
        painter.fillPath(path, self.text_color)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ale Abbey Monastery Brewery Tycoon Calculator")
        self.resize(1200, 800)  # Modificata la dimensione della finestra

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

        # Nuovo codice per il titolo con outline
        title_label = OutlinedLabel(" Ale Abbey Monastery Brewery Tycoon Calculator", self)
        title_label.setFont(QFont("Alegreya", 28, QFont.Bold))
        title_label.setMinimumHeight(70)
        title_label.setTextColor(QColor("#FFD700"))  # Oro
        title_label.setOutlineColor(QColor("#000000"))  # Nero
        title_label.setOutlineThickness(3)
        main_layout.setContentsMargins(10, 20, 10, 10)
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Frame principale per la sezione ingredienti
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
        ingredients_label = OutlinedLabel(" Lista Ingredienti", self)
        ingredients_label.setFont(QFont("Alegreya", 18, QFont.Bold))
        ingredients_label.setMinimumHeight(60)
        ingredients_label.setTextColor(QColor("#FFD700"))
        ingredients_label.setOutlineColor(QColor("#000000"))
        ingredients_label.setOutlineThickness(3)
        ingredients_layout.addWidget(ingredients_label)
        ingredients_layout.setSpacing(3)
        ingredients_layout.setContentsMargins(10, 10, 10, 0)

        # Header delle colonne
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 0, 5, 5)
        header_layout.setSpacing(0)
        
        # Header colonna sinistra
        left_header = QHBoxLayout()
        left_header.setContentsMargins(0, 0, 0, 0)
        left_header.setSpacing(0)
        
        left_header.addStretch(3)
        left_header.addWidget(QLabel("Sbloccato", self), stretch=1, alignment=Qt.AlignCenter)
        left_header.addWidget(QLabel("Obbligatorio", self), stretch=1, alignment=Qt.AlignCenter)
        
        # Header colonna destra
        right_header = QHBoxLayout()
        right_header.setContentsMargins(0, 0, 0, 0)
        right_header.setSpacing(0)
        
        right_header.addStretch(3)
        right_header.addWidget(QLabel("Sbloccato", self), stretch=1, alignment=Qt.AlignCenter)
        right_header.addWidget(QLabel("Obbligatorio", self), stretch=1, alignment=Qt.AlignCenter)
        
        # Aggiunta degli header al layout principale
        header_separator = QFrame()
        header_separator.setFrameShape(QFrame.VLine)
        header_separator.setFrameShadow(QFrame.Sunken)
        header_separator.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0);
                width: 1px;
            }
        """)
        
        header_layout.addLayout(left_header)
        header_layout.addSpacing(10)
        header_layout.addWidget(header_separator)
        header_layout.addSpacing(5)
        header_layout.addLayout(right_header)
        
        # Stile per le label degli header
        for label in self.findChildren(QLabel):
            if label.parent() == self and label.text() in ["Sbloccato", "Obbligatorio"]:
                label.setStyleSheet("""
                    color: white;
                    font-family: Alegreya;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 2px;
                """)
                
        ingredients_layout.addLayout(header_layout)
                # Area scrollabile per gli ingredienti
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QScrollBar {
                width: 0px;
                height: 0px;
                background: transparent;
            }
        """)
        # Widget per la lista degli ingredienti
        ing_widget = QWidget()
        list_layout = QHBoxLayout(ing_widget)
        list_layout.setContentsMargins(5, 5, 5, 5)
        list_layout.setSpacing(0)
        
        # Creiamo due colonne
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        
        # Dizionari per tenere traccia dei checkbox
        self.unlocked_checkboxes = {}
        self.required_checkboxes = {}

        # Calcoliamo il punto medio della lista ingredienti
        mid_point = len(INGREDIENTI_ORDINE_SBLOCCO) // 2
        
        # Creazione delle righe per ogni ingrediente
        for i, ingr in enumerate(INGREDIENTI_ORDINE_SBLOCCO):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(0)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            ingr_label = QLabel(ingr, self)
            ingr_label.setStyleSheet("""
                color: white;
                font-family: Alegreya;
                font-size: 12px;
                font-weight: bold;
            """)
            ingr_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            row_layout.addWidget(ingr_label, stretch=3, alignment=Qt.AlignLeft)

            unlocked_cb = QCheckBox(self)
            unlocked_cb.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-family: Alegreya;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            if ingr in ALWAYS_AVAILABLE:
                unlocked_cb.setChecked(True)
                unlocked_cb.setEnabled(False)
            self.unlocked_checkboxes[ingr] = unlocked_cb
            row_layout.addWidget(unlocked_cb, stretch=1, alignment=Qt.AlignCenter)

            required_cb = QCheckBox(self)
            required_cb.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-family: Alegreya;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            self.required_checkboxes[ingr] = required_cb
            row_layout.addWidget(required_cb, stretch=1, alignment=Qt.AlignCenter)

            if i < mid_point:
                left_column.addLayout(row_layout)
            else:
                right_column.addLayout(row_layout)

        content_separator = QFrame()
        content_separator.setFrameShape(QFrame.VLine)
        content_separator.setFrameShadow(QFrame.Sunken)
        content_separator.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 100);
                width: 1px;
            }
        """)
        
        list_layout.addLayout(left_column)
        list_layout.addSpacing(10)
        list_layout.addWidget(content_separator)
        list_layout.addSpacing(15)
        list_layout.addLayout(right_column)

        scroll_area.setWidget(ing_widget)
        ingredients_layout.addWidget(scroll_area)
        main_layout.addWidget(ingredients_frame)

        # Layout inferiore per Virtù e Risultati
        bottom_layout = QHBoxLayout()

        # Pannello Virtù
        virtues_frame = QFrame(self)
        virtues_frame.setFrameShape(QFrame.StyledPanel)
        virtues_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 10px;
            }
            QLabel {
                background: none;
                background-color: transparent;
            }
        """)
        virtues_shadow = QGraphicsDropShadowEffect()
        virtues_shadow.setBlurRadius(15)
        virtues_shadow.setXOffset(3)
        virtues_shadow.setYOffset(3)
        virtues_shadow.setColor(QColor(0, 0, 0, 160))
        virtues_frame.setGraphicsEffect(virtues_shadow)

        self.parameters = ["gusto", "colore", "gradazione", "schiuma"]
        self.sliders = {}
        self.param_labels = {}

        virtues_layout = QVBoxLayout(virtues_frame)
        # Titolo principale del pannello Virtù con OutlinedLabel
        virtues_title = OutlinedLabel(" Virtù", self)
        virtues_title.setFont(QFont("Alegreya", 20, QFont.Bold))
        virtues_title.setMinimumHeight(40)
        virtues_title.setTextColor(QColor("#FFD700"))
        virtues_title.setOutlineColor(QColor("#000000"))
        virtues_title.setOutlineThickness(2)
        virtues_layout.addWidget(virtues_title)
        
        # Aggiunta degli slider nel pannello Virtù
        for param in self.parameters:
            param_layout = QVBoxLayout()
            
            # Creiamo un widget container per il titolo
            title_container = QWidget()
            title_layout = QHBoxLayout(title_container)  # Assegniamo subito il parent
            title_layout.setSpacing(10)
            title_layout.setContentsMargins(0, 0, 0, 0)
            
            # Titolo del parametro con OutlinedLabel
            title_label = OutlinedLabel(f" {param.capitalize()}", self)
            title_label.setFont(QFont("Alegreya", 14, QFont.Bold))
            title_label.setMinimumHeight(30)
            title_label.setTextColor(QColor("#FFD700"))
            title_label.setOutlineColor(QColor("#000000"))
            title_label.setOutlineThickness(2)
            title_layout.addWidget(title_label)
            
            title_layout.addStretch()
            
            range_label = QLabel("min 0 - max 10", self)
            range_label.setStyleSheet("""
                color: white;
                font-family: Alegreya;
                font-size: 14px;
                font-weight: bold;
            """)
            title_layout.addWidget(range_label)
            self.param_labels[param] = range_label
            
            param_layout.addWidget(title_container)
            
            slider = SquareSlider(0, 10, self)
            slider.valueChanged.connect(lambda low, high, p=param: self.updateParameterLabel(p, low, high))
            param_layout.addWidget(slider)
            self.sliders[param] = slider
            
            virtues_layout.addLayout(param_layout)
        # Pannello Risultati
        results_frame = QFrame(self)
        results_frame.setFrameShape(QFrame.StyledPanel)
        results_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 10px;
            }
        """)
        results_shadow = QGraphicsDropShadowEffect()
        results_shadow.setBlurRadius(15)
        results_shadow.setXOffset(3)
        results_shadow.setYOffset(3)
        results_shadow.setColor(QColor(0, 0, 0, 160))
        results_frame.setGraphicsEffect(results_shadow)

        results_layout = QVBoxLayout(results_frame)

        # Compute button
        self.compute_button = QPushButton("Trova Ricetta", self)
        icon = QIcon("search_icon.png")
        self.compute_button.setIcon(icon)
        self.compute_button.setStyleSheet("""
            QPushButton {
            font-size: 20px;
            font-family: Alegreya;
            padding: 8px;
            background-color: rgba(30, 30, 30, 180);
            color: #FFD700;  /* Colore oro */
            border-radius: 10px;
            font-weight: bold;
            border: 3px solid black;  /* Bordo nero per l'outline */
            text-shadow: -3px -3px 0 #000,  
                        3px -3px 0 #000,
                       -3px  3px 0 #000,
                        3px  3px 0 #000,
                       -3px  0   0 #000,
                        3px  0   0 #000,
                        0   -3px 0 #000,
                        0    3px 0 #000;  /* Crea l'effetto outline */
          }
          QPushButton:hover {
              background-color: rgba(50, 50, 50, 200);
          }
          QPushButton:pressed {
              background-color: rgba(20, 20, 20, 200);
              padding-top: 10px;
          }
          QPushButton:disabled {
              background-color: rgba(30, 30, 30, 100);
              color: rgba(255, 215, 0, 128);  /* Oro semi-trasparente quando disabilitato */
          }
""")
        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setBlurRadius(15)
        button_shadow.setXOffset(3)
        button_shadow.setYOffset(3)
        button_shadow.setColor(QColor(0, 0, 0, 160))
        self.compute_button.setGraphicsEffect(button_shadow)
        self.compute_button.clicked.connect(self.compute_combination)
        results_layout.addWidget(self.compute_button)

        # Results text area
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
        results_layout.addWidget(self.result_text)

        # Aggiunta dei pannelli al layout inferiore
        bottom_layout.addWidget(virtues_frame, 3)
        bottom_layout.addWidget(results_frame, 4)

        # Aggiunta del layout inferiore al layout principale
        main_layout.addLayout(bottom_layout)

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
        unlocked_ingredients = []
        
        for ingr in ingredienti:
            if self.required_checkboxes[ingr].isChecked():
                required_ingredients.append(ingredienti.index(ingr))
            if self.unlocked_checkboxes[ingr].isChecked() or ingr in ALWAYS_AVAILABLE:
                unlocked_ingredients.append(ingredienti.index(ingr))

        ranges = {}
        for param in self.parameters:
            slider = self.sliders[param]
            ranges[param] = (slider.low(), slider.high())

        self.worker = CalculationWorker(required_ingredients, ranges, unlocked_ingredients)
        self.worker.finished.connect(self.on_calculation_complete)
        self.worker.start()

    def on_calculation_complete(self, result):
        self.spinner.stop()
        self.loading_widget.hide()
    
        quantities, values, stats = result
    
        if quantities:
            result_text = "✅ Combinazione ottimale trovata!\n\n"
            result_text += f"⏱️ Tempo impiegato: {stats['execution_time']:.2f} secondi\n\n"
        
            result_text += "Ingredienti da utilizzare:\n"
            result_text += "-" * 30 + "\n"
            for ingr, qty in zip(ingredienti, quantities):
                if qty > 0:
                    result_text += f"{ingr}: {qty} unità\n"
        
            result_text += "\nValori ottenuti:\n"
            result_text += "-" * 30 + "\n"
            for key, val in values.items():
                result_text += f"{key.capitalize()}: {val:.1f}\n"
        
            result_text += "\nStatistiche della ricerca:\n"
            result_text += "-" * 30 + "\n"
            result_text += f"Combinazioni teoriche: {stats['total_combinations']:,}\n"
            result_text += f"Combinazioni esaminate: {stats['examined_combinations']:,}\n"
            result_text += f"Scartate per limite totale > 25: {stats['skipped_total']:,}\n"
            result_text += f"Scartate per ingredienti obbligatori: {stats['skipped_required']:,}\n"
            result_text += f"Scartate per valori fuori range: {stats['skipped_range']:,}\n"
            result_text += f"Combinazioni valide: {stats['valid_combinations']:,}\n"
        else:
            result_text = "❌ Nessuna combinazione valida trovata!\n\n"
            result_text += f"⏱️ Tempo di ricerca: {stats['execution_time']:.2f} secondi\n"
            result_text += "Possibili cause:\n"
            result_text += "-" * 30 + "\n"
            result_text += "• Range dei valori troppo restrittivo\n"
            result_text += "• Troppi ingredienti obbligatori selezionati\n"
            result_text += "• Combinazione di requisiti impossibile da soddisfare\n"
            result_text += "• Ingredienti necessari non ancora sbloccati\n\n"
        
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
        
            result_text += "\nStatistiche della ricerca:\n"
            result_text += "-" * 30 + "\n"
            result_text += f"Combinazioni teoriche: {stats['total_combinations']:,}\n"
            result_text += f"Combinazioni esaminate: {stats['examined_combinations']:,}\n"

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
