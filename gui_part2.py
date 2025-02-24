class BeerRecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Beer Recipe Solver")
        self.root.geometry("1000x600")  # Risoluzione della finestra

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configuriamo le colonne e le righe per distribuire lo spazio uniformemente
        for i in range(3):
            main_frame.columnconfigure(i, weight=1)
        for i in range(5):
            main_frame.rowconfigure(i, weight=1)

        ingredients_frame = ttk.LabelFrame(main_frame, text="Ingredienti", padding="10")
        ingredients_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        sliders_frame = ttk.LabelFrame(main_frame, text="Virtù", padding="10")
        sliders_frame.grid(row=1, column=1, sticky="ew", padx=100)  # Aumentiamo il padding a sinistra per centrare meglio

        # Ingredient Checkbuttons
        self.required_ingredients = []
        for idx, ingredient in enumerate(ingredienti):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(ingredients_frame, text=ingredient, variable=var)
            chk.grid(row=0, column=idx, sticky=tk.W)
            self.required_ingredients.append((idx, var))

        # Sliders for parameters
        self.range_sliders = {}
        self.single_value_sliders = {}
        self.mode_buttons = {}
        parameters = ["gusto", "colore", "gradazione", "schiuma"]
        self.min_labels = {}
        self.max_labels = {}

        for idx, param in enumerate(parameters):
            slider_label = ttk.Label(sliders_frame, text=f"{param.capitalize()}")
            slider_label.grid(row=idx * 3, column=0, padx=5, pady=(5, 2), columnspan=2)  # Riduciamo il padding superiore e inferiore

            min_label = ttk.Label(sliders_frame, text="Min: 0")
            min_label.grid(row=idx * 3 + 2, column=0, padx=5)
            self.min_labels[param] = min_label

            max_label = ttk.Label(sliders_frame, text="Max: 10")
            max_label.grid(row=idx * 3 + 2, column=1, padx=5)
            self.max_labels[param] = max_label

            range_slider = RangeSlider(sliders_frame, param, from_=0, to=10, steps=10, width=800, height=50, min_label=min_label, max_label=max_label)
            range_slider.grid(row=idx * 3 + 1, column=0, padx=5, pady=(2, 5), columnspan=2)  # Riduciamo il padding superiore e inferiore
            self.range_sliders[param] = range_slider

            single_value_slider = SingleValueSlider(sliders_frame, param, from_=0, to=10, steps=10, width=800, height=50, label=min_label)
            single_value_slider.grid(row=idx * 3 + 1, column=0, padx=5, pady=(2, 5), columnspan=2)
            single_value_slider.grid_remove()
            self.single_value_sliders[param] = single_value_slider

            mode_button = ttk.Button(sliders_frame, text="Range", command=self.create_toggle_command(single_value_slider, range_slider, param))
            mode_button.grid(row=idx * 3 + 2, column=0, padx=5, sticky=tk.W)
            self.mode_buttons[param] = mode_button

        # Search Button
        self.search_button = ttk.Button(main_frame, text="Search", command=self.search)
        self.search_button.grid(row=2, column=1, pady=10)

        # Result Textbox
        self.result_text = tk.Text(main_frame, width=80, height=10)
        self.result_text.grid(row=3, column=0, columnspan=3, pady=10)

    def create_toggle_command(self, single_value_slider, range_slider, param):
        def toggle():
            if single_value_slider.winfo_ismapped():
                single_value_slider.grid_remove()
                range_slider.grid()
                self.mode_buttons[param].config(text="Range")
                self.min_labels[param].config(text=f"Min: {int(range_slider.get_min_value())}")
                self.max_labels[param].config(text=f"Max: {int(range_slider.get_max_value())}")
            else:
                range_slider.grid_remove()
                single_value_slider.grid()
                self.mode_buttons[param].config(text="Valore Specifico")
                self.min_labels[param].config(text=f"Valore: {int(single_value_slider.get_value())}")
                self.max_labels[param].config(text="")
        return toggle

    def search(self):
        required_ingredients = [idx for idx, var in self.required_ingredients if var.get()]

        ranges = {
            "gusto": (self.range_sliders["gusto"].get_min_value(), self.range_sliders["gusto"].get_max_value()) if self.range_sliders["gusto"].winfo_ismapped() else (self.single_value_sliders["gusto"].get_value(), self.single_value_sliders["gusto"].get_value()),
            "colore": (self.range_sliders["colore"].get_min_value(), self.range_sliders["colore"].get_max_value()) if self.range_sliders["colore"].winfo_ismapped() else (self.single_value_sliders["colore"].get_value(), self.single_value_sliders["colore"].get_value()),
            "gradazione": (self.range_sliders["gradazione"].get_min_value(), self.range_sliders["gradazione"].get_max_value()) if self.range_sliders["gradazione"].winfo_ismapped() else (self.single_value_sliders["gradazione"].get_value(), self.single_value_sliders["gradazione"].get_value()),
            "schiuma": (self.range_sliders["schiuma"].get_min_value(), self.range_sliders["schiuma"].get_max_value()) if self.range_sliders["schiuma"].winfo_ismapped() else (self.single_value_sliders["schiuma"].get_value(), self.single_value_sliders["schiuma"].get_value()),
        }

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