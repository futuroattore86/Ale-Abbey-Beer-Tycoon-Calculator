import tkinter as tk
from tkinter import ttk
from calculator import ingredienti, find_optimal_combination

# A scrollable frame class for Tkinter that supports mouse wheel scrolling
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.bind_events()

    def bind_events(self):
        # Bind mousewheel events for Windows and macOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # For Linux using Button-4 and Button-5
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")


class RangeSlider(tk.Canvas):
    def __init__(self, parent, parameter, from_=0, to=10, steps=10, min_label=None, max_label=None, **kwargs):
        # Set default dimensions; these will update on resize.
        self.default_width = 850
        self.default_height = 100
        kwargs["width"] = self.default_width
        kwargs["height"] = self.default_height
        super().__init__(parent, **kwargs)
        self.parameter = parameter
        self.from_ = from_
        self.to = to
        self.steps = steps

        # Gaps on both sides for centering
        self.left_gap = 20
        self.right_gap = 20
        self.slider_width = 10    # Marker width
        self.slider_height = 28   # Marker height
        self.value_font = ('Helvetica', 10)
        self.min_label = min_label
        self.max_label = max_label

        # Store current slider values (in same scale as from_ and to)
        self.min_val = from_
        self.max_val = to
        self.single_val = from_

        # Variables for current drawn dimensions (will be set on resize)
        self.current_width = self.default_width
        self.current_height = self.default_height
        self._calculate_dimensions()
        
        # Bind events for dragging and for resizing
        self.bind("<B1-Motion>", self.update_position)
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<Configure>", self.on_resize)

        self.single_value_mode = False
        # Draw initial slider
        self.redraw()

    def _calculate_dimensions(self):
        # Use current width and height from the widget
        self.current_width = self.winfo_width() if self.winfo_width() > 0 else self.default_width
        self.current_height = self.winfo_height() if self.winfo_height() > 0 else self.default_height

        # Calculate effective slider area (based on left/right gaps)
        self.start_x = self.left_gap + self.slider_width / 2
        self.end_x = self.current_width - self.right_gap - self.slider_width / 2
        self.available_width = self.end_x - self.start_x
        self.step_size = self.available_width / self.steps

        # Set track vertical positions (we use fixed margins for track)
        self.track_top = 40
        self.track_bottom = self.current_height - 40

    def redraw(self):
        # Clear all drawings and re-draw slider based on current dimensions and stored values.
        self.delete("all")
        self._calculate_dimensions()

        # Draw slider track
        self.create_rectangle(
            self.start_x, self.track_top,
            self.end_x, self.track_bottom,
            fill="lightgrey", outline=""
        )
        # Draw the range bar (colored part)
        self.range_bar = self.create_rectangle(
            self.start_x, self.track_top,
            self.end_x, self.track_bottom,
            fill="lightgreen", outline=""
        )
        # Draw border for aesthetics
        self.create_rectangle(
            self.start_x - 1, self.track_top - 1,
            self.end_x + 1, self.track_bottom + 1,
            outline="black"
        )
        # Draw ticks and labels
        self.draw_ticks()

        # Calculate marker vertical coordinates (centered vertically)
        marker_top = (self.current_height - self.slider_height) / 2
        marker_bottom = (self.current_height + self.slider_height) / 2

        # Redraw markers at their correct positions based on stored values
        if self.single_value_mode:
            # For single value mode, use self.single_val
            x = self.start_x + ((self.single_val - self.from_) / (self.to - self.from_)) * self.available_width
            self.min_marker = self.create_rectangle(
                x - self.slider_width / 2, marker_top,
                x + self.slider_width / 2, marker_bottom,
                fill="blue", outline="black", tags="min_marker"
            )
        else:
            # In range mode, position min and max markers
            x_min = self.start_x + ((self.min_val - self.from_) / (self.to - self.from_)) * self.available_width
            x_max = self.start_x + ((self.max_val - self.from_) / (self.to - self.from_)) * self.available_width
            self.min_marker = self.create_rectangle(
                x_min - self.slider_width / 2, marker_top,
                x_min + self.slider_width / 2, marker_bottom,
                fill="blue", outline="black", tags="min_marker"
            )
            self.max_marker = self.create_rectangle(
                x_max - self.slider_width / 2, marker_top,
                x_max + self.slider_width / 2, marker_bottom,
                fill="red", outline="black", tags="max_marker"
            )
        # Raise markers above other elements
        self.tag_raise("min_marker")
        self.tag_raise("max_marker")

    def draw_ticks(self):
        tick_top = self.track_bottom + 5  # Below the track
        for i in range(self.steps + 1):
            x_pos = self.start_x + i * self.step_size
            self.create_line(x_pos, tick_top, x_pos, tick_top + 10, fill="black")
            value_label = self.from_ + i * ((self.to - self.from_) / self.steps)
            self.create_text(x_pos, tick_top + 20,
                             text=str(int(value_label)),
                             fill="black", font=self.value_font)

    def on_resize(self, event):
        # Callback when the canvas is resized
        self.redraw()

    def start_drag(self, event):
        self.drag_data = {
            "x": event.x,
            "y": event.y,
            "item": self.find_closest(event.x, event.y)[0]
        }

    def update_position(self, event):
        x = event.x
        if x < self.start_x: 
            x = self.start_x
        elif x > self.end_x:
            x = self.end_x
        # Snap x to nearest tick position
        step = round((x - self.start_x) / self.step_size) * self.step_size + self.start_x

        if self.single_value_mode:
            self.update_single_value_mode(step)
        else:
            self.update_range_mode(step)
        self.update_range()

    def update_single_value_mode(self, step):
        marker_top = (self.current_height - self.slider_height) / 2
        marker_bottom = (self.current_height + self.slider_height) / 2
        self.coords(
            self.min_marker,
            step - self.slider_width / 2,
            marker_top,
            step + self.slider_width / 2,
            marker_bottom
        )
        self.single_val = self.from_ + ((step - self.start_x) / self.available_width) * (self.to - self.from_)
        self.single_val = max(self.from_, min(self.single_val, self.to))
        if self.min_label:
            self.min_label.config(text=f"Valore: {int(self.single_val)}")
        if self.max_label:
            self.max_label.config(text="")

    def update_range_mode(self, step):
        marker_top = (self.current_height - self.slider_height) / 2
        marker_bottom = (self.current_height + self.slider_height) / 2
        if self.drag_data["item"] == self.min_marker:
            old_min_val = self.min_val
            new_min_val = self.from_ + ((step - self.start_x) / self.available_width) * (self.to - self.from_)
            new_min_val = max(self.from_, min(new_min_val, self.to))
            if new_min_val >= self.max_val:
                new_min_val = old_min_val
                step = self.start_x + ((old_min_val - self.from_) / (self.to - self.from_)) * self.available_width
            self.coords(
                self.min_marker,
                step - self.slider_width / 2,
                marker_top,
                step + self.slider_width / 2,
                marker_bottom
            )
            self.min_val = new_min_val
            if self.min_label:
                self.min_label.config(text=f"Min: {int(self.min_val)}")
        elif self.drag_data["item"] == self.max_marker:
            old_max_val = self.max_val
            new_max_val = self.from_ + ((step - self.start_x) / self.available_width) * (self.to - self.from_)
            new_max_val = max(self.from_, min(new_max_val, self.to))
            if new_max_val <= self.min_val:
                new_max_val = old_max_val
                step = self.start_x + ((old_max_val - self.from_) / (self.to - self.from_)) * self.available_width
            self.coords(
                self.max_marker,
                step - self.slider_width / 2,
                marker_top,
                step + self.slider_width / 2,
                marker_bottom
            )
            self.max_val = new_max_val
            if self.max_label:
                self.max_label.config(text=f"Max: {int(self.max_val)}")

    def update_range(self):
        marker_top = (self.current_height - self.slider_height) / 2
        marker_bottom = (self.current_height + self.slider_height) / 2
        if self.single_value_mode:
            self.coords(self.range_bar, self.start_x, self.track_top, 
                        self.coords(self.min_marker)[2], self.track_bottom)
        else:
            self.coords(self.range_bar, self.coords(self.min_marker)[2],
                        self.track_top, self.coords(self.max_marker)[0], self.track_bottom)
        self.tag_raise(self.range_bar)
        self.tag_raise("min_marker")
        self.tag_raise("max_marker")
        if self.min_val == self.max_val:
            self.itemconfig("min_marker", fill="purple")
            self.itemconfig("max_marker", fill="purple")
        else:
            self.itemconfig("min_marker", fill="blue")
            self.itemconfig("max_marker", fill="red")

    def get_min_value(self):
        return int(self.min_val)

    def get_max_value(self):
        return int(self.max_val)

    def get_single_value(self):
        return int(self.single_val)


class SingleValueSlider(tk.Canvas):
    def __init__(self, parent, parameter, from_=0, to=10, steps=10, label=None, **kwargs):
        self.default_width = 850
        self.default_height = 100
        kwargs["width"] = self.default_width
        kwargs["height"] = self.default_height
        super().__init__(parent, **kwargs)
        self.parameter = parameter
        self.from_ = from_
        self.to = to
        self.steps = steps
        self.left_gap = 20
        self.right_gap = 20
        self.slider_width = 10
        self.slider_height = 28
        self.value_font = ('Helvetica', 10)
        self.label = label

        self.val = from_
        self.current_width = self.default_width
        self.current_height = self.default_height
        self._calculate_dimensions()

        self.bind("<B1-Motion>", self.update_position)
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<Configure>", self.on_resize)

        self.redraw()

    def _calculate_dimensions(self):
        self.current_width = self.winfo_width() if self.winfo_width() > 0 else self.default_width
        self.current_height = self.winfo_height() if self.winfo_height() > 0 else self.default_height
        self.start_x = self.left_gap + self.slider_width / 2
        self.end_x = self.current_width - self.right_gap - self.slider_width / 2
        self.available_width = self.end_x - self.start_x
        self.step_size = self.available_width / self.steps

        self.track_top = 40
        self.track_bottom = self.current_height - 40

    def redraw(self):
        self.delete("all")
        self._calculate_dimensions()
        self.create_rectangle(
            self.start_x, self.track_top,
            self.end_x, self.track_bottom,
            fill="lightgrey", outline=""
        )
        self.draw_ticks()
        marker_top = (self.current_height - self.slider_height) / 2
        marker_bottom = (self.current_height + self.slider_height) / 2
        x = self.start_x + ((self.val - self.from_) / (self.to - self.from_)) * self.available_width
        self.marker = self.create_rectangle(
            x - self.slider_width / 2, marker_top,
            x + self.slider_width / 2, marker_bottom,
            fill="blue", outline="black", tags="marker"
        )
        self.tag_raise("marker")

    def draw_ticks(self):
        tick_top = self.track_bottom + 5
        for i in range(self.steps + 1):
            x_pos = self.start_x + i * self.step_size
            self.create_line(x_pos, tick_top, x_pos, tick_top + 10, fill="black")
            value_label = self.from_ + i * ((self.to - self.from_) / self.steps)
            self.create_text(x_pos, tick_top + 20,
                             text=str(int(value_label)),
                             fill="black", font=self.value_font)

    def on_resize(self, event):
        self.redraw()

    def start_drag(self, event):
        self.drag_data = {
            "x": event.x,
            "y": event.y,
            "item": self.find_closest(event.x, event.y)[0]
        }

    def update_position(self, event):
        x = event.x
        if x < self.start_x:
            x = self.start_x
        elif x > self.end_x:
            x = self.end_x
        step = round((x - self.start_x) / self.step_size) * self.step_size + self.start_x
        marker_top = (self.current_height - self.slider_height) / 2
        marker_bottom = (self.current_height + self.slider_height) / 2
        self.coords(
            self.marker,
            step - self.slider_width / 2,
            marker_top,
            step + self.slider_width / 2,
            marker_bottom
        )
        offset = round((step - self.start_x) / self.step_size)
        self.val = self.from_ + offset * ((self.to - self.from_) / self.steps)
        self.val = max(self.from_, min(self.val, self.to))
        if self.label:
            self.label.config(text=f"Valore: {int(self.val)}")

    def get_value(self):
        return int(self.val)


class BeerRecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Beer Recipe Solver")
        # Set a moderate initial window resolution
        self.root.geometry("900x600")
        self.create_widgets()

    def create_widgets(self):
        scrollable = ScrollableFrame(self.root)
        scrollable.pack(fill="both", expand=True)
        main_frame = ttk.Frame(scrollable.scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        for i in range(3):
            main_frame.columnconfigure(i, weight=1)
        for i in range(6):
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
            slider_label.grid(row=idx*3, column=0, padx=5, pady=(5, 2), columnspan=2)
            min_label = ttk.Label(sliders_frame, text="Min: 0")
            min_label.grid(row=idx*3+2, column=0, padx=5)
            self.min_labels[param] = min_label
            max_label = ttk.Label(sliders_frame, text="Max: 10")
            max_label.grid(row=idx*3+2, column=1, padx=5)
            self.max_labels[param] = max_label

            range_slider = RangeSlider(sliders_frame, param, from_=0, to=10, steps=10,
                                        min_label=min_label, max_label=max_label)
            range_slider.grid(row=idx*3+1, column=0, padx=5, pady=(2,5), columnspan=2)
            self.range_sliders[param] = range_slider

            single_value_slider = SingleValueSlider(sliders_frame, param, from_=0, to=10, steps=10,
                                                    label=min_label)
            single_value_slider.grid(row=idx*3+1, column=0, padx=5, pady=(2,5), columnspan=2)
            single_value_slider.grid_remove()
            self.single_value_sliders[param] = single_value_slider

            mode_button = ttk.Button(sliders_frame, text="Range",
                                     command=self.create_toggle_command(single_value_slider, range_slider, param))
            mode_button.grid(row=idx*3+2, column=0, padx=5, sticky=tk.W)
            self.mode_buttons[param] = mode_button

        self.search_button = ttk.Button(main_frame, text="Search", command=self.search)
        self.search_button.grid(row=5, column=1, pady=10)
        self.result_text = tk.Text(main_frame, width=80, height=10)
        self.result_text.grid(row=6, column=0, columnspan=3, pady=10)

    def create_toggle_command(self, single_value_slider, range_slider, param):
        def toggle():
            if single_value_slider.winfo_ismapped():
                single_value_slider.grid_remove()
                range_slider.grid()
                self.mode_buttons[param].config(text="Range")
                self.min_labels[param].config(text=f"Min: {range_slider.get_min_value()}")
                self.max_labels[param].config(text=f"Max: {range_slider.get_max_value()}")
            else:
                range_slider.grid_remove()
                single_value_slider.grid()
                self.mode_buttons[param].config(text="Valore Specifico")
                self.min_labels[param].config(text=f"Valore: {int(single_value_slider.get_value())}")
                self.max_labels[param].config(text="")
        return toggle

    def search(self):
        required_ingredients = [idx for idx, var in self.required_ingredients if var.get()]
        ranges = {}
        for p in ["gusto", "colore", "gradazione", "schiuma"]:
            if self.range_sliders[p].winfo_ismapped():
                ranges[p] = (self.range_sliders[p].get_min_value(), self.range_sliders[p].get_max_value())
            else:
                val = self.single_value_sliders[p].get_value()
                ranges[p] = (val, val)
        quantities, values, counter = find_optimal_combination(required_ingredients, ranges)
        self.result_text.delete(1.0, tk.END)
        if quantities:
            result = "Quantità trovate:\n"
            for ingredient, quantity in zip(ingredienti, quantities):
                result += f"{quantity} unità di {ingredient}\n"
            result += f"Valori: {values}\n"
            result += f"Numero di combinazioni esaminate: {counter}\n"
        else:
            result = "Nessuna combinazione valida trovata dopo aver esaminato tutte le possibilità."
            result += f"\nNumero di combinazioni esaminate: {counter}\n"
        self.result_text.insert(tk.END, result)

if __name__ == "__main__":
    root = tk.Tk()
    app = BeerRecipeApp(root)
    root.mainloop()
