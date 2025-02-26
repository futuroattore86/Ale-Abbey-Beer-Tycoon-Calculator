# Coefficients for each ingredient
coefficients = {
    'gusto': [0.4, 0.8, 1.6, 0.8, 2.0, 1.0, 2.5, -1.0, 0.5, 1.0, 2.0,
              1.5, 1.5, 0.5, -0.5, 1.5, 0.3, 1.5, 0.8, 1.2, 1.6,
              0.5, 1.0, 1.5, 1.0, 1.0, 1.0, 1.5, -0.5, -1.0, 0.0, 0.5],
    'colore': [0.3, 1.2, 2.0, -0.3, 1.0, 3.0, 0.5, -0.5, 1.0, 0.3, 2.0,
               1.0, 1.5, 0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               -0.3, 0.0, 0.0, 2.0, 0.0, 1.0, -1.0, 0.0, -1.0, 0.0, -1.0],
    'gradazione': [1.0, 0.5, 0.0, 0.4, -0.5, -1.0, 0.5, 2.0, 1.5, 1.0, 0.5,
                   0.5, 0.5, -1.0, 0.0, -1.0, 2.0, 0.5, 0.0, 0.0, 0.0, 0.0,
                   -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.2],
    'schiuma': [0.5, 0.8, 0.0, 2.0, 1.5, 0.5, 0.5, -1.0, -0.5, 0.0, 0.5,
                0.5, 0.0, -0.5, 0.0, 0.0, 0.5, 1.0, 0.5, 0.5, 1.0, 0.0,
                -0.5, 0.0, 0.0, -1.0, -1.0, 0.0, 1.5, 0.0, 0.0, 2.0]
}

# Full list of ingredients
ingredienti = [
    'Malto Chiaro', 'Malto Ambrato', 'Malto Marrone', 'Malto di Frumento',
    'Malto di Segale', 'Malto Tostato', 'Malto Affumicato', 'Zucchero',
    'Zucchero Scuro Candito', 'Miele', 'Bacche', 'Uva', 'Ciliegie',
    'Lievito Standard', 'Lievito Lager', 'Lievito Estereo', 'Lievito Forte',
    'Lievito Selvaggio', 'Luppolo Classico', 'Luppolo Cascadus', 'Luppolo Magnum',
    'Gruit', 'Eucalipto', 'Semi di Coriandolo', 'Scorza di Arancia', 'Caffè',
    'Pepe', 'Zucca', 'Fecola di Frumento', 'Fiocchi di Mais', 'Nutrienti per Lievito',
    'Fiocchi di Frumento'
]

# Order of unlocking ingredients in the game
INGREDIENTI_ORDINE_SBLOCCO = [
    'Malto Chiaro', 'Lievito Standard', 'Gruit', 'Malto Marrone',
    'Malto Ambrato', 'Luppolo Classico', 'Miele', 'Eucalipto', 'Lievito Forte',
    'Malto di Frumento', 'Lievito Estereo', 'Pepe', 'Zucchero Scuro Candito',
    'Fecola di Frumento', 'Zucchero', 'Ciliegie', 'Bacche', 'Luppolo Cascadus',
    'Luppolo Magnum', 'Malto Tostato', 'Lievito Selvaggio', 'Lievito Lager',
    'Malto di Segale', 'Fiocchi di Frumento', 'Semi di Coriandolo',
    'Scorza di Arancia', 'Uva', 'Zucca', 'Caffè', 'Fiocchi di Mais',
    'Nutrienti per Lievito', 'Malto Affumicato'
]

# Always available ingredients and the unlockable ones.
ALWAYS_AVAILABLE = ['Malto Chiaro', 'Lievito Standard']
UNLOCKABLE_INGREDIENTS = [ingr for ingr in INGREDIENTI_ORDINE_SBLOCCO if ingr not in ALWAYS_AVAILABLE]

from functools import lru_cache

@lru_cache(maxsize=1024)
def calculate_values_incremental(base_values_tuple, ingredient_idx, quantity_delta):
    """
    Incrementally calculates new virtual values (gusto, colore, gradazione, schiuma).
    base_values_tuple is a tuple (gusto, colore, gradazione, schiuma).
    """
    return (
        base_values_tuple[0] + quantity_delta * coefficients['gusto'][ingredient_idx],
        base_values_tuple[1] + quantity_delta * coefficients['colore'][ingredient_idx],
        base_values_tuple[2] + quantity_delta * coefficients['gradazione'][ingredient_idx],
        base_values_tuple[3] + quantity_delta * coefficients['schiuma'][ingredient_idx]
    )

def calculate_base_values(base_quantities):
    """
    Calculates the initial virtual values from the provided quantities.
    """
    return {
        'gusto': sum(q * c for q, c in zip(base_quantities, coefficients['gusto'])),
        'colore': sum(q * c for q, c in zip(base_quantities, coefficients['colore'])),
        'gradazione': sum(q * c for q, c in zip(base_quantities, coefficients['gradazione'])),
        'schiuma': sum(q * c for q, c in zip(base_quantities, coefficients['schiuma']))
    }

def calculate_score(values, ranges):
    """
    Calculates a score based on the closeness of virtual values to the desired ranges.
    A small tolerance is applied (0.05) for borderline values.
    Adjust the base multiplier (10) and bonus multiplier (100) as needed.
    """
    tolerance = 0.05
    score = 0
    for param in ['gusto', 'colore', 'gradazione', 'schiuma']:
        low, high = ranges[param]
        current = values[param]
        if (low - tolerance) <= current <= (high + tolerance):
            score += current * 10
            normalized = (current - low) / (high - low) if (high - low) != 0 else 1
            score += normalized * 100
        else:
            score -= 10000
    return score

def get_ingredient_index(ingredient_name):
    """
    Returns the index of an ingredient given its name.
    """
    try:
        return ingredienti.index(ingredient_name)
    except ValueError:
        return -1

def worker_process(params):
    """
    Worker routine for parallel search.
    Each worker explores a slice of the search space based on the units for the first ingredient.
    """
    variable_indices = params['variable_indices']
    ranges = params['ranges']
    required_ingredients = params['required_ingredients']
    worker_id = params['worker_id']
    num_workers = params['num_workers']
    
    local_results = {
        "best_score": -float('inf'),
        "best_quantities": None,
        "best_values": None,
        "stats": {
            "examined_combinations": 0,
            "skipped_total": 0,
            "skipped_required": 0,
            "skipped_range": 0,
            "valid_combinations": 0
        }
    }
    
    def has_required_ingredients(quantities):
        return all(quantities[idx] >= 1 for idx in required_ingredients)
    
    # Define the subrange for the first ingredient (0-9) for this worker.
    start_value = (worker_id * 10) // num_workers
    end_value = ((worker_id + 1) * 10) // num_workers
    
    def generate_combinations(partial, current_sum, position, current_values_tuple):
        if current_sum > 25:
            local_results["stats"]["skipped_total"] += 1
            return
            
        if position == len(variable_indices):
            local_results["stats"]["examined_combinations"] += 1
            quantities = [0] * len(ingredienti)
            for idx, qty in zip(variable_indices, partial):
                quantities[idx] = qty
            if not has_required_ingredients(quantities):
                local_results["stats"]["skipped_required"] += 1
                return
            current_vals = {
                'gusto': current_values_tuple[0],
                'colore': current_values_tuple[1],
                'gradazione': current_values_tuple[2],
                'schiuma': current_values_tuple[3]
            }
            in_range = True
            for param in ['gusto', 'colore', 'gradazione', 'schiuma']:
                low, high = ranges[param]
                if not (low <= current_vals[param] <= high):
                    in_range = False
                    break
            if not in_range:
                local_results["stats"]["skipped_range"] += 1
                return
            
            local_results["stats"]["valid_combinations"] += 1
            score = calculate_score(current_vals, ranges)
            if score > local_results["best_score"]:
                local_results["best_score"] = score
                local_results["best_quantities"] = quantities.copy()
                local_results["best_values"] = current_vals.copy()
                print("\nNuova migliore combinazione trovata (Worker {}):".format(worker_id))
                for i, qty in enumerate(quantities):
                    if qty > 0:
                        print(f"{ingredienti[i]}: {qty}")
                print("Valori: Gusto={:.2f}, Colore={:.2f}, Gradazione={:.2f}, Schiuma={:.2f}".format(
                    current_vals['gusto'], current_vals['colore'], current_vals['gradazione'], current_vals['schiuma']))
                print("Score: {:.2f}".format(score))
            return
            
        if position == 0:
            value_range = range(start_value, end_value)
        else:
            value_range = range(10)
            
        for qty in value_range:
            new_values_tuple = calculate_values_incremental(
                current_values_tuple,
                variable_indices[position],
                qty
            )
            generate_combinations(
                partial + [qty],
                current_sum + qty,
                position + 1,
                new_values_tuple
            )
    
    initial_values = (0, 0, 0, 0)
    generate_combinations([], 0, 0, initial_values)
    return local_results

from multiprocessing import Pool, cpu_count
from time import time

def find_optimal_combination(required_ingredients, ranges, unlocked_ingredients):
    """
    Finds the optimal combination that meets:
     - A total unit limit of 25.
     - At least one unit for each required ingredient.
     - Virtual values (gusto, colore, gradazione, schiuma) within the desired ranges.
    The search is parallelized across multiple processes.
    """
    start_time = time()
    
    print("\nDEBUG INFO:")
    print("Ingredienti richiesti (almeno 1 unità):", [ingredienti[i] for i in required_ingredients])
    print("Ingredienti sbloccati ricevuti:", [ingredienti[i] for i in unlocked_ingredients])
    
    always_available_indices = [ingredienti.index(ingr) for ingr in ALWAYS_AVAILABLE]
    print("\nDEBUG - Indici e ingredienti:")
    print("Ingredienti sempre disponibili:", [ingredienti[i] for i in always_available_indices])
    print("Ingredienti sbloccati:", [ingredienti[i] for i in unlocked_ingredients])
    
    unlocked_set = set(unlocked_ingredients)
    unlocked_set.update(always_available_indices)
    usable_indices = sorted(list(unlocked_set))
    print("Tutti gli ingredienti utilizzabili:", [ingredienti[i] for i in usable_indices])
    
    variable_indices = usable_indices
    print("\nIngredienti variabili totali:", len(variable_indices))
    print([ingredienti[i] for i in variable_indices])
    
    total_theoretical_combinations = 10 ** len(variable_indices)
    print("\nGenerazione combinazioni:")
    print("- Numero ingredienti variabili:", len(variable_indices))
    print("- Range per ogni ingrediente: 0-9")
    print(f"- Combinazioni teoriche totali: {total_theoretical_combinations:,}")
    
    num_processes = min(cpu_count(), 4)
    print("\nUtilizzo", num_processes, "processi paralleli")
    
    worker_params = []
    for i in range(num_processes):
        params = {
            'variable_indices': variable_indices,
            'ranges': ranges,
            'required_ingredients': required_ingredients,
            'worker_id': i,
            'num_workers': num_processes
        }
        worker_params.append(params)
    
    shared_results = {
        "best_score": -float('inf'),
        "best_quantities": None,
        "best_values": None,
        "stats": {
            "examined_combinations": 0,
            "skipped_total": 0,
            "skipped_required": 0,
            "skipped_range": 0,
            "valid_combinations": 0
        }
    }
    
    with Pool(processes=num_processes) as pool:
        worker_results = pool.map(worker_process, worker_params)
    
    for result in worker_results:
        if result["best_score"] > shared_results["best_score"]:
            shared_results["best_score"] = result["best_score"]
            shared_results["best_quantities"] = result["best_quantities"]
            shared_results["best_values"] = result["best_values"]
        for key in result["stats"]:
            shared_results["stats"][key] += result["stats"][key]
    
    end_time = time()
    shared_results["stats"].update({
        "total_combinations": total_theoretical_combinations,
        "execution_time": end_time - start_time,
        "best_score": shared_results["best_score"] if shared_results["best_score"] > -float('inf') else None
    })
    
    print("\nStatistiche della ricerca:")
    print("-" * 30)
    print(f"Combinazioni teoriche: {shared_results['stats']['total_combinations']:,}")
    print(f"Combinazioni esaminate: {shared_results['stats']['examined_combinations']:,}")
    print(f"Scartate per limite totale > 25: {shared_results['stats']['skipped_total']:,}")
    print(f"Scartate per ingredienti obbligatori: {shared_results['stats']['skipped_required']:,}")
    print(f"Scartate per valori fuori range: {shared_results['stats']['skipped_range']:,}")
    print(f"Combinazioni valide: {shared_results['stats']['valid_combinations']:,}")
    print(f"\nTempo di esecuzione: {shared_results['stats']['execution_time']:.2f} secondi")
    
    return shared_results["best_quantities"], shared_results["best_values"], shared_results["stats"]
