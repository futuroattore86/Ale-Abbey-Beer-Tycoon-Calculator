from itertools import product
from time import time
from multiprocessing import Pool, cpu_count
from functools import lru_cache

# Coefficienti per ogni ingrediente
coefficients = {
    'gusto': [0.4, 0.8, 1.6, 0.8, 2.0, 1.0, 2.5, -1.0, 0.5, 1.0, 2.0, 1.5, 1.5, 0.5, -0.5, 1.5, 0.3, 1.5, 0.8, 1.2, 1.6, 0.5, 1.0, 1.5, 1.0, 1.0, 1.0, 1.5, -0.5, -1.0, 0.0, 0.5],
    'colore': [0.3, 1.2, 2.0, -0.3, 1.0, 3.0, 0.5, -0.5, 1.0, 0.3, 2.0, 1.0, 1.5, 0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.3, 0.0, 0.0, 2.0, 0.0, 1.0, -1.0, 0.0, -1.0, 0.0, -1.0],
    'gradazione': [1.0, 0.5, 0.0, 0.4, -0.5, -1.0, 0.5, 2.0, 1.5, 1.0, 0.5, 0.5, 0.5, -1.0, 0.0, -1.0, 2.0, 0.5, 0.0, 0.0, 0.0, 0.0, -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.2],
    'schiuma': [0.5, 0.8, 0.0, 2.0, 1.5, 0.5, 0.5, -1.0, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5, 0.0, 0.0, 0.5, 1.0, 0.5, 0.5, 1.0, 0.0, -0.5, 0.0, 0.0, -1.0, -1.0, 0.0, 1.5, 0.0, 0.0, 2.0]
}

# Lista completa degli ingredienti
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

# Ordine di sblocco degli ingredienti nel gioco
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

ALWAYS_AVAILABLE = ['Malto Chiaro', 'Lievito Standard']
UNLOCKABLE_INGREDIENTS = [ingr for ingr in INGREDIENTI_ORDINE_SBLOCCO if ingr not in ALWAYS_AVAILABLE]

@lru_cache(maxsize=1024)
def calculate_values_incremental(base_values_tuple, ingredient_idx, quantity_delta):
    """
    Versione cacheable del calcolo incrementale dei valori
    """
    return {
        'gusto': base_values_tuple[0] + quantity_delta * coefficients['gusto'][ingredient_idx],
        'colore': base_values_tuple[1] + quantity_delta * coefficients['colore'][ingredient_idx],
        'gradazione': base_values_tuple[2] + quantity_delta * coefficients['gradazione'][ingredient_idx],
        'schiuma': base_values_tuple[3] + quantity_delta * coefficients['schiuma'][ingredient_idx]
    }

def calculate_base_values(base_quantities):
    """
    Calcola i valori iniziali per una data configurazione base
    """
    return {
        'gusto': sum(q * c for q, c in zip(base_quantities, coefficients['gusto'])),
        'colore': sum(q * c for q, c in zip(base_quantities, coefficients['colore'])),
        'gradazione': sum(q * c for q, c in zip(base_quantities, coefficients['gradazione'])),
        'schiuma': sum(q * c for q, c in zip(base_quantities, coefficients['schiuma']))
    }

def calculate_score(values, ranges):
    """
    Nuovo sistema di scoring che dà più peso ai valori che si arrotondano ai massimi
    """
    score = 0
    for param in ['gusto', 'colore', 'gradazione', 'schiuma']:
        min_value = ranges[param][0]
        max_value = ranges[param][1]
        current_value = values[param]
        
        if min_value <= current_value <= max_value:
            # Base score per essere nel range
            score += 1000
            
            # Bonus per l'arrotondamento
            game_rounded_value = int(current_value + 0.99)
            target_rounded = int(max_value)
            if game_rounded_value >= target_rounded:
                score += 2000
            
            # Bonus per vicinanza al massimo
            proximity = (current_value - min_value) / (max_value - min_value)
            score += proximity * 1500
        else:
            score -= 10000
            
    return score
def worker_process(params):
    """
    Funzione worker per il processing parallelo.
    params è un dizionario contenente tutti i parametri necessari.
    Qui la divisione del lavoro è ottimizzata basandosi sul primo ingrediente.
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
        """Verifica che tutti gli ingredienti richiesti abbiano almeno 1 unità."""
        return all(quantities[idx] >= 1 for idx in required_ingredients)

    # Determina il range di valori per il primo ingrediente in base al worker.
    start_value = (worker_id * 10) // num_workers
    end_value = ((worker_id + 1) * 10) // num_workers

    def generate_combinations(partial, current_sum, position, current_values):
        if current_sum > 25:
            local_results["stats"]["skipped_total"] += 1
            return
            
        if position == len(variable_indices):
            # Verifica la combinazione solo a livello di modulo del numero di worker
            if local_results["stats"]["examined_combinations"] % num_workers != worker_id:
                return
            local_results["stats"]["examined_combinations"] += 1
            
            quantities = [0] * len(ingredienti)
            for idx, qty in zip(variable_indices, partial):
                quantities[idx] = qty
            
            if not has_required_ingredients(quantities):
                local_results["stats"]["skipped_required"] += 1
                return
            
            if not (ranges['gusto'][0] <= current_values['gusto'] <= ranges['gusto'][1] and 
                    ranges['colore'][0] <= current_values['colore'] <= ranges['colore'][1] and 
                    ranges['gradazione'][0] <= current_values['gradazione'] <= ranges['gradazione'][1] and 
                    ranges['schiuma'][0] <= current_values['schiuma'] <= ranges['schiuma'][1]):
                local_results["stats"]["skipped_range"] += 1
                return
                
            local_results["stats"]["valid_combinations"] += 1
            score = calculate_score(current_values, ranges)
            
            if score > local_results["best_score"]:
                local_results["best_score"] = score
                local_results["best_quantities"] = quantities.copy()
                local_results["best_values"] = current_values.copy()
                
                print(f"\nNuova migliore combinazione trovata (Worker {worker_id}):")
                print("Ingredienti utilizzati:")
                num_ingredients = 0
                for i, qty in enumerate(quantities):
                    if qty > 0:
                        print(f"{ingredienti[i]}: {qty}")
                        num_ingredients += 1
                print(f"Numero totale ingredienti: {num_ingredients}")
                print(f"Somma totale unità: {current_sum}")
                print(f"Valori: Gusto={current_values['gusto']:.2f}, "
                      f"Colore={current_values['colore']:.2f}, "
                      f"Gradazione={current_values['gradazione']:.2f}, "
                      f"Schiuma={current_values['schiuma']:.2f}")
                print(f"Score: {score:.2f}")
            return
            
        # Se siamo al primo ingrediente, limitiamo il range al sottoinsieme assegnato al worker
        if position == 0:
            value_range = range(start_value, end_value)
        else:
            value_range = range(10)
            
        for qty in value_range:
            new_values = calculate_values_incremental(
                (current_values['gusto'], current_values['colore'],
                 current_values['gradazione'], current_values['schiuma']),
                variable_indices[position],
                qty
            )
            generate_combinations(
                partial + [qty],
                current_sum + qty,
                position + 1,
                new_values
            )
    
    initial_values = {'gusto': 0, 'colore': 0, 'gradazione': 0, 'schiuma': 0}
    generate_combinations([], 0, 0, initial_values)
    
    return local_results

def find_optimal_combination(required_ingredients, ranges, unlocked_ingredients):
    """
    Trova la combinazione ottimale di ingredienti che soddisfa i requisiti
    utilizzando parallelizzazione, caching e calcolo incrementale.
    """
    from multiprocessing import Pool, cpu_count  # In caso in cui non sia già importato
    start_time = time()
    
    print("\nDEBUG INFO:")
    print(f"Ingredienti richiesti (almeno 1 unità): {[ingredienti[i] for i in required_ingredients]}")
    print(f"Ingredienti sbloccati ricevuti: {[ingredienti[i] for i in unlocked_ingredients]}")
    
    # Debug per gli indici utilizzabili
    always_available_indices = [ingredienti.index(ingr) for ingr in ALWAYS_AVAILABLE]
    print("\nDEBUG - Indici e ingredienti:")
    print("Ingredienti sempre disponibili:", [ingredienti[i] for i in always_available_indices])
    print("Ingredienti sbloccati:", [ingredienti[i] for i in unlocked_ingredients])
    
    # Unisci gli ingredienti sbloccati con quelli sempre disponibili
    unlocked_set = set(unlocked_ingredients)
    unlocked_set.update(always_available_indices)
    usable_indices = sorted(list(unlocked_set))
    print("Tutti gli ingredienti utilizzabili:", [ingredienti[i] for i in usable_indices])
    
    # Ora tutti gli ingredienti utilizzabili sono variabili
    variable_indices = usable_indices
    print(f"\nIngredienti variabili totali: {len(variable_indices)}")
    print([ingredienti[i] for i in variable_indices])
    
    total_theoretical_combinations = 10**len(variable_indices)
    print(f"\nGenerazione combinazioni:")
    print(f"- Numero ingredienti variabili: {len(variable_indices)}")
    print(f"- Range per ogni ingrediente: 0-9")
    print(f"- Combinazioni teoriche totali: {total_theoretical_combinations:,}")
    
    # Limitiamo l'overhead impostando il numero di processi a 4
    num_processes = min(cpu_count(), 4)
    print(f"\nUtilizzo {num_processes} processi paralleli")
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
    
    # Combina i risultati di tutti i worker
    for result in worker_results:
        if result["best_score"] > shared_results["best_score"]:
            shared_results["best_score"] = result["best_score"]
            shared_results["best_quantities"] = result["best_quantities"]
            shared_results["best_values"] = result["best_values"]
        for stat in result["stats"]:
            shared_results["stats"][stat] += result["stats"][stat]
    
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

def get_ingredient_index(ingredient_name):
    """
    Ottiene l'indice di un ingrediente dal suo nome.
    """
    try:
        return ingredienti.index(ingredient_name)
    except ValueError:
        return -1
