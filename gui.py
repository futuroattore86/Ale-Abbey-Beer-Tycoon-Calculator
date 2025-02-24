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
        self.width = 800
        self.height = 50
        self.slider_width = 10
        self.slider_height = 28
        self.value_font = ('Helvetica', 10)
        self.min_label = min_label
        self.max_label = max_label

        self.min_val = from_
        self.max_val = to
        self.single_val = from_

        self.step_size = (self.width - self.slider_width) / (self.steps - 1)

        self.background_rect = self.create_rectangle(
            self.slider_width / 2, 10, self.width - self.slider_width / 2, self.height - 10, fill="lightgrey", outline=""
        )

        self.range_bar = self.create_rectangle(
            self.slider_width / 2, 10, self.width - self.slider_width / 2, self.height - 10, fill="lightgreen", outline=""
        )

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
            if step >= max_marker_coords[0] - self.step_size:
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
            if step <= min_marker_coords[2] + self.step_size:
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
        self.coords(
            self.range_bar,
            self.coords(self.min_marker)[0] + self.slider_width / 2 - 6,
            10,
            self.coords(self.max_marker)[2] - self.slider_width / 2 + 6,
            self.height - 10
        )

class SingleValueSlider(tk.Canvas):
    def __init__(self, parent, parameter, from_=0, to=10, steps=10, label=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parameter = parameter
        self.from_ = from_
        self.to = to
        self.steps = steps
        self.width = 800
        self.height = 50
        self.slider_width = 10
        self.slider_height = 28
        self.value_font = ('Helvetica', 10)
        self.label = label

        self.val = from_

        self.step_size = (self.width - self.slider_width) / (self.steps - 1)

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

class BeerRecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Beer Recipe Solver")
        self.root.geometry("1000x600")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        for i in range(3):
            main_frame.columnconfigure(i, weight=1)
        for i in range(5):
            main_frame.rowconfigure(i, weight=1)

        ingredients_frame = ttk.LabelFrame(main_frame, text="Ingredienti", padding="10")
        ingredients_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        sliders_frame = ttk.LabelFrame(main_frame, text="Virtù", padding="10")
        sliders_frame.grid(row=1, column=1, sticky="ew", padx=100)

        self.required_ingredients = []
        for idx, ingredient in enumerate(ingredienti):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(ingredients_frame, text=ingredient, variable=var)
            chk.grid(row=0, column=idx, sticky=tk.W)
            self.required_ingredients.append((idx, var))

        self.range_sliders = {}
        self.single_value_sliders = {}
        self.mode_buttons = {}
        parameters = ["gusto", "colore", "gradazione", "schiuma"]
        self.min_labels = {}
        self.max_labels = {}

        for idx, param in enumerate(parameters):
            slider_label = ttk.Label(sliders_frame, text=f"{param.capitalize()}")
            slider_label.grid(row=idx * 3, column=0, padx=5, pady=(5, 2), columnspan=2)

            min_label = ttk.Label(sliders_frame, text="Min: 0")
            min_label.grid(row=idx * 3 + 2, column=0, padx=5)
            self.min_labels[param] = min_label

            max_label = ttk.Label(sliders_frame, text="Max: 10")
            max_label.grid(row=idx * 3 + 2, column=1, padx=5)
            self.max_labels[param] = max_label

            range_slider = RangeSlider(sliders_frame, param, from_=0, to=10, steps=10, width=800, height=50, min_label=min_label, max_label=max_label)
            range_slider.grid(row=idx * 3 + 1, column=0, padx=5, pady=(2, 5), columnspan=2)
            self.range_sliders[param] = range_slider

            single_value_slider = SingleValueSlider(sliders_frame, param, from_=0, to=10, steps=10, width=800, height=50, label=min_label)
            single_value_slider.grid(row=idx * 3 + 1, column=0, padx=5, pady=(2, 5), columnspan=2)
            single_value_slider.grid_remove()
            self.single_value_sliders[param] = single_value_slider

            mode_button = ttk.Button(sliders_frame, text="Range", command=self.create_toggle_command(single_value_slider, range_slider, param))
            mode_button.grid(row=idx * 3 + 2, column=0, padx=5, sticky=tk.W)
            self.mode_buttons[param] = mode_button

        self.search_button = ttk.Button(main_frame, text="Search", command=self.search)
        self.search_button.grid(row=2, column=1, pady=10)

        self.result_text = tk.Text(main_frame, wrap="word", width=100, height=15)
        self.result_text.grid(row=3, column=0, columnspan=3, pady=10)

    def create_toggle_command(self, single_value_slider, range_slider, param):
        def toggle():
            if range_slider.winfo_ismapped():
                range_slider.grid_remove()
                single_value_slider.grid()
                self.mode_buttons[param].config(text="Single Value")
                range_slider.single_value_mode = True
            else:
                single_value_slider.grid_remove()
                range_slider.grid()
                self.mode_buttons[param].config(text="Range")
                range_slider.single_value_mode = False
        return toggle

    def search(self):
        selected_ingredients = [ingr[0] for ingr in self.required_ingredients if ingr[1].get()]
        parameters = {}
        for param, slider in self.range_sliders.items():
            if slider.single_value_mode:
                parameters[param] = slider.single_val
            else:
                parameters[param] = (slider.min_val, slider.max_val)

        results = find_optimal_combination(selected_ingredients, parameters)
        self.result_text.delete("1.0", tk.END)
        for result in results:
            self.result_text.insert(tk.END, result + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = BeerRecipeApp(root)
    root.mainloop()