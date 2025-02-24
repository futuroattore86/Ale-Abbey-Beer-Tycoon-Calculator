import tkinter as tk
from tkinter import ttk
from calculator import ingredienti, find_optimal_combination

class RangeSlider(tk.Canvas):
    def __init__(self, parent, parameter, from_=0, to=10, steps=10, min_label=None, max_label=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parameter = parameter
        self.from_ = from_
        self.to = to
        self.steps = steps
        self.width = 800  # Larghezza dello slider aumentata
        self.height = 50  # Altezza dello slider
        self.slider_width = 10  # Larghezza delle maniglie
        self.slider_height = 28  # Altezza delle maniglie leggermente inferiore a quella dello slider
        self.value_font = ('Helvetica', 10)
        self.min_label = min_label
        self.max_label = max_label

        self.min_val = from_
        self.max_val = to
        self.single_val = from_

        self.step_size = (self.width - self.slider_width) / self.steps  # Calcolare la distanza percorsa per ogni step

        # Aggiungiamo uno sfondo per delineare l'area dello slider
        self.background_rect = self.create_rectangle(
            self.slider_width / 2, 10, self.width - self.slider_width / 2, self.height - 10, fill="lightgrey", outline=""
        )

        self.range_bar = self.create_rectangle(
            self.slider_width / 2, 10, self.width - self.slider_width / 2, self.height - 10, fill="lightgreen", outline=""
        )

        # Disegniamo un bordo intorno agli slider
        self.slider_border = self.create_rectangle(
            self.slider_width / 2 - 1, 9, self.width - self.slider_width / 2 + 1, self.height - 9, outline="black"
        )

        self.min_marker = self.create_rectangle(
            self.slider_width / 2 - self.slider_width / 2 + 6,
            (self.height - self.slider_height) / 2,
            self.slider_width / 2 + self.slider_width / 2 + 6,
            (self.height + self.slider_height) / 2,
            fill="blue",
            outline="black",
            tags="min_marker"
        )
        self.max_marker = self.create_rectangle(
            self.width - self.slider_width / 2 - self.slider_width / 2 - 6,
            (self.height - self.slider_height) / 2,
            self.width - self.slider_width / 2 + self.slider_width / 2 - 6,
            (self.height + self.slider_height) / 2,
            fill="red",
            outline="black",
            tags="max_marker"
        )

        self.tag_raise(self.min_marker)
        self.tag_raise(self.max_marker)

        self.bind("<B1-Motion>", self.update_position)
        self.bind("<ButtonPress-1>", self.start_drag)

        self.single_value_mode = False

        self.update_range()

    def start_drag(self, event):
        self.drag_data = {"x": event.x, "y": event.y, "item": self.find_closest(event.x, event.y)[0]}

    def update_position(self, event):
        x = event.x
        if x < self.slider_width / 2:
            x = self.slider_width / 2
        elif x > self.width - self.slider_width / 2:
            x = self.width - self.slider_width / 2

        step = round((x - self.slider_width / 2) / self.step_size) * self.step_size + self.slider_width / 2

        if self.single_value_mode:
            self.update_single_value_mode(step)
        else:
            self.update_range_mode(step)

        self.update_range()

    def update_single_value_mode(self, step):
        self.coords(
            self.min_marker,
            step - self.slider_width / 2 + 6,
            (self.height - self.slider_height) / 2,
            step + self.slider_width / 2 + 6,
            (self.height + self.slider_height) / 2,
        )
        self.single_val = self.from_ + ((step - self.slider_width / 2) / (self.width - self.slider_width)) * (self.to - self.from_)
        self.single_val = max(self.from_, min(self.single_val, self.to))
        if self.min_label:
            self.min_label.config(text=f"Valore: {int(self.single_val)}")
        if self.max_label:
            self.max_label.config(text="")

    def update_range_mode(self, step):
        if self.drag_data["item"] == self.min_marker:
            max_marker_coords = self.coords(self.max_marker)
            if step >= max_marker_coords[0]:
                step = max_marker_coords[0] - self.step_size
            self.coords(
                self.min_marker,
                step - self.slider_width / 2 + 6,
                (self.height - self.slider_height) / 2,
                step + self.slider_width / 2 + 6,
                (self.height + self.slider_height) / 2,
            )
            self.min_val = self.from_ + ((step - self.slider_width / 2) / (self.width - self.slider_width)) * (self.to - self.from_)
            self.min_val = max(self.from_, min(self.min_val, self.to))
            if self.min_label:
                self.min_label.config(text=f"Min: {int(self.min_val)}")
        elif self.drag_data["item"] == self.max_marker:
            min_marker_coords = self.coords(self.min_marker)
            if step <= min_marker_coords[2]:
                step = min_marker_coords[2] + self.step_size
            self.coords(
                self.max_marker,
                step - self.slider_width / 2 - 6,
                (self.height - self.slider_height) / 2,
                step + self.slider_width / 2 - 6,
                (self.height + self.slider_height) / 2,
            )
            self.max_val = self.from_ + ((step - self.slider_width / 2) / (self.width - self.slider_width)) * (self.to - self.from_)
            self.max_val = max(self.from_, min(self.max_val, self.to))
            if self.max_label:
                self.max_label.config(text=f"Max: {int(self.max_val)}")

    def update_range(self):
        if self.single_value_mode:
            self.coords(self.range_bar, self.slider_width / 2, 10, self.coords(self.min_marker)[2], self.height - 10)
        else:
            self.coords(self.range_bar, self.coords(self.min_marker)[2], 10, self.coords(self.max_marker)[0], self.height - 10)
        self.tag_raise(self.range_bar)
        self.tag_raise(self.min_marker)
        self.tag_raise(self.max_marker)

        if self.min_val == self.max_val:
            self.itemconfig(self.min_marker, fill="purple")
            self.itemconfig(self.max_marker, fill="purple")
        else:
            self.itemconfig(self.min_marker, fill="blue")
            self.itemconfig(self.max_marker, fill="red")

    def toggle_mode(self):
        self.single_value_mode = not self.single_value_mode
        if self.single_value_mode:
            self.itemconfig(self.min_marker, fill="blue")
            self.coords(self.max_marker, self.coords(self.min_marker))
            self.single_val = self.min_val = self.max_val
            if self.min_label:
                self.min_label.config(text=f"Valore: {int(self.single_val)}")
            if self.max_label:
                self.max_label.config(text="")
        else:
            self.min_val = self.from_
            self.max_val = self.to
            self.coords(
                self.min_marker,
                self.slider_width / 2 - self.slider_width / 2 + 6,
                (self.height - self.slider_height) / 2,
                self.slider_width / 2 + self.slider_width / 2 + 6,
                (self.height + self.slider_height) / 2
            )
            self.coords(
                self.max_marker,
                self.width - self.slider_width / 2 - self.slider_width / 2 - 6,
                (self.height - self.slider_height) / 2,
                self.width - self.slider_width / 2 + self.slider_width / 2 - 6,
                (self.height + self.slider_height) / 2
            )
            if self.min_label:
                self.min_label.config(text=f"Min: {int(self.min_val)}")
            if self.max_label:
                self.max_label.config(text=f"Max: {int(self.max_val)}")
            self.update_range()

    def get_min_value(self):
        return int(self.min_val)

    def get_max_value(self):
        return int(self.max_val)

    def get_single_value(self):
        return int(self.single_val)


class SingleValueSlider(tk.Canvas):
    def __init__(self, parent, parameter, from_=0, to=10, steps=10, label=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parameter = parameter
        self.from_ = from_
        self.to = to
        self.steps = steps
        self.width = 800  # Larghezza dello slider aumentata
        self.height = 50  # Altezza dello slider
        self.slider_width = 10  # Larghezza delle maniglie
        self.slider_height = 28  # Altezza delle maniglie leggermente inferiore a quella dello slider
        self.value_font = ('Helvetica', 10)
        self.label = label

        self.val = from_

        self.step_size = (self.width - self.slider_width) / (self.steps)  # Calcolare la distanza percorsa per ogni step

        # Aggiungiamo uno sfondo per delineare l'area dello slider
        self.background_rect = self.create_rectangle(
            self.slider_width / 2, 10, self.width - self.slider_width / 2, self.height - 10, fill="lightgrey", outline=""
        )

        self.marker = self.create_rectangle(
            self.slider_width / 2 - self.slider_width / 2 + 6,
            (self.height - self.slider_height) / 2,
            self.slider_width / 2 + self.slider_width / 2 + 6,
            (self.height + self.slider_height) / 2,
            fill="blue",
            outline="black",
            tags="marker"
        )

        self.tag_raise(self.marker)

        self.bind("<B1-Motion>", self.update_position)
        self.bind("<ButtonPress-1>", self.start_drag)

    def start_drag(self, event):
        self.drag_data = {"x": event.x, "y": event.y, "item": self.find_closest(event.x, event.y)[0]}

    def update_position(self, event):
        x = event.x
        if x < self.slider_width / 2:
            x = self.slider_width / 2
        elif x > self.width - self.slider_width / 2:
            x = self.width - self.slider_width / 2

        step = round((x - self.slider_width / 2) / self.step_size) * self.step_size + self.slider_width / 2

        # Assicurarsi che il marker non vada oltre il limite visualizzato
        if step > self.width - self.slider_width / 2:
            step = self.width - self.slider_width / 2

        self.coords(
            self.marker,
            step - self.slider_width / 2 + 6,
            (self.height - self.slider_height) / 2,
            step + self.slider_width / 2 + 6,
            (self.height + self.slider_height) / 2,
        )
        self.val = self.from_ + ((step - self.slider_width / 2) / (self.width - self.slider_width)) * (self.to - self.from_)
        self.val = max(self.from_, min(self.val, self.to))
        if self.label:
            self.label.config(text=f"Valore: {int(self.val)}")

    def get_value(self):
        return int(self.val)