#!/usr/bin/env python3
"""
Calculator per trovare la combinazione ottimale di ingredienti (fino ad un totale di 25 unità)
in base ai parametri "gusto", "colore", "gradazione" e "schiuma", con penalità in caso di valori fuori
dei range previsti.
Lo spazio delle combinazioni viene "appiattito" e diviso in modo equo tra 8 worker.
Questo file viene consultato dall'interfaccia grafica per gestire i parametri richiesti di calcolo.
"""

# Limite massimo di unità per ciascun ingrediente
MAX_QUANTITY = 5

# Coefficienti per ogni ingrediente
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

# Ordine in cui vengono sbloccati gli ingredienti nel gioco
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

# Ingredienti sempre disponibili e sbloccabili
ALWAYS_AVAILABLE = ['Malto Chiaro', 'Lievito Standard']
UNLOCKABLE_INGREDIENTS = [ingr for ingr in INGREDIENTI_ORDINE_SBLOCCO if ingr not in ALWAYS_AVAILABLE]

def index_to_combination(index, length, base):
    """
    Converte un indice (in base 10) in una combinazione 
    (lista di 'length' cifre) usando base = MAX_QUANTITY + 1.
    Ogni cifra rappresenta la quantità per l'ingrediente corrispondente.
    """
    combo = [0] * length
    for pos in range(length - 1, -1, -1):
        combo[pos] = index % base
        index //= base
    return combo

def calculate_values(quantities):
    """
    Calcola i valori virtuali (gusto, colore, gradazione, schiuma) 
    come somma di quantità * coefficienti.
    """
    values = {'gusto': 0, 'colore': 0, 'gradazione': 0, 'schiuma': 0}
    for i, qty in enumerate(quantities):
        values['gusto']      += qty * coefficients['gusto'][i]
        values['colore']     += qty * coefficients['colore'][i]
        values['gradazione'] += qty * coefficients['gradazione'][i]
        values['schiuma']    += qty * coefficients['schiuma'][i]
    return values

def calculate_score(values, ranges):
    """
    Calcola lo score basandosi sulla vicinanza dei valori ai range desiderati
    e applica una tolleranza di 0.05. 
    Modifica il controllo dell'upper bound per permettere, ad esempio, che 
    un range 1-3 includa valori fino a 3.99 (ossia, < 4.0).
    Valori fuori dal range sono penalizzati di -10000.
    """
    tolerance = 0.05
    score = 0
    for param in ['gusto', 'colore', 'gradazione', 'schiuma']:
        low, high = ranges[param]
        current = values[param]
        # Modifica: consenti valori < (high + 1.0) anziché <= high
        if (low - tolerance) <= current < (high + 1.0):
            score += current * 10
            normalized = (current - low) / (high - low) if (high - low) != 0 else 1
            score += normalized * 100
        else:
            score -= 10000
    return score

def meets_required(quantities, required_indices):
    """
    Ritorna True se, per tutti gli indici in required_indices,
    la quantità corrispondente è almeno 1.
    """
    return all(quantities[i] >= 1 for i in required_indices)

def normalize_ranges(ranges):
    """
    Normalizza 'ranges' in un dizionario con chiavi 'gusto', 'colore', 'gradazione', 'schiuma'.
    Se 'ranges' è già un dizionario, lo restituisce invariato.
    Se è una lista o tuple, si assume l'ordine indicato.
    """
    if isinstance(ranges, dict):
        return ranges
    elif isinstance(ranges, (tuple, list)):
        keys = ['gusto', 'colore', 'gradazione', 'schiuma']
        if len(ranges) < len(keys):
            raise ValueError("Non sono stati forniti abbastanza valori per i range.")
        return {keys[i]: ranges[i] for i in range(len(keys))}
    else:
        raise ValueError("Tipo non valido per il parametro ranges.")

def worker_process(params):
    """
    Worker che elabora un intervallo dello spazio "appiattito" delle combinazioni.
    Per ogni indice, converte l'indice in una combinazione per gli ingredienti sbloccati,
    applica i vincoli sul totale (<= 25), sugli ingredienti richiesti e sui range dei valori.
    """
    start_index   = params["start_index"]
    end_index     = params["end_index"]
    variable_indices = params["variable_indices"]   # Indici degli ingredienti sbloccati
    required_indices = params["required_indices"]       # Indici degli ingredienti obbligatori
    total_units_constraint = 25
    ranges = normalize_ranges(params["ranges"])
    worker_id = params["worker_id"]

    best_score = -float('inf')
    best_quantities = None
    best_values = None
    stats = {
        "examined": 0,
        "skipped_total": 0,
        "skipped_required": 0,
        "skipped_range": 0,
        "valid": 0
    }
    base = MAX_QUANTITY + 1
    total_vars = len(variable_indices)

    for idx in range(start_index, end_index):
        # Genera una combinazione relativa agli ingredienti sbloccati
        combo = index_to_combination(idx, total_vars, base)
        # Inizializza il vettore delle quantità per tutti gli ingredienti a 0
        quantities = [0] * len(ingredienti)
        for pos, ingr_idx in enumerate(variable_indices):
            quantities[ingr_idx] = combo[pos]
        stats["examined"] += 1

        # Verifica il vincolo del totale unità
        if sum(quantities) > total_units_constraint:
            stats["skipped_total"] += 1
            continue

        # Verifica che siano presenti gli ingredienti obbligatori
        if not meets_required(quantities, required_indices):
            stats["skipped_required"] += 1
            continue

        values = calculate_values(quantities)
        # Verifica che i valori rientrino nei range specificati
        valid = True
        for param in ['gusto', 'colore', 'gradazione', 'schiuma']:
            low, high = ranges[param]
            # Modifica: consentire valori < (high + 1.0)
            if not (low <= values[param] < high + 1.0):
                valid = False
                break
        if not valid:
            stats["skipped_range"] += 1
            continue

        stats["valid"] += 1
        score = calculate_score(values, ranges)
        if score > best_score:
            best_score = score
            best_quantities = quantities.copy()
            best_values = values.copy()
            # Stampa di debug del nuovo best trovato (opzionale)
            print(f"\nNew best combination found (Worker {worker_id}):")
            for i, qty in enumerate(quantities):
                if qty > 0:
                    print(f"{ingredienti[i]}: {qty}")
            values_str = ", ".join(f"{k.capitalize()}={values[k]:.2f}" for k in values)
            print(f"Values: {values_str}")
            print(f"Score: {score:.2f}")
    
    return {"best_score": best_score, "best_quantities": best_quantities, "best_values": best_values, "stats": stats}

def find_optimal_combination(required_ingredients, ranges, unlocked_ingredients):
    """
    Cerca la combinazione ottimale che rispetti:
      - Totale unità <= 25;
      - Almeno una unità per ogni ingrediente richiesto;
      - Valori (gusto, colore, gradazione, schiuma) nei range specificati.
    Lo spazio delle combinazioni teoriche viene calcolato in base al numero di ingredienti sbloccati,
    e suddiviso in 8 worker. Vengono stampate le statistiche iniziali (inclusi i range usati)
    prima di iniziare la ricerca.
    """
    from multiprocessing import Pool
    from time import time

    ranges = normalize_ranges(ranges)

    # Debug: stampa dei range usati per il calcolo
    print("DEBUG: Range in uso:")
    for param, (low, high) in ranges.items():
        print(f"  {param.capitalize()}: {low} - {high}  (valori accettati: [{low}, {high + 1.0}))")

    # Combina gli ingredienti sbloccati con quelli sempre disponibili.
    # Per preservare l'ordine della GUI, usa l'ordine di unlocked_ingredients
    usable_indices = []
    for idx in unlocked_ingredients:
        if idx not in usable_indices:
            usable_indices.append(idx)
    for ingr in ALWAYS_AVAILABLE:
        idx = ingredienti.index(ingr)
        if idx not in usable_indices:
            usable_indices.append(idx)

    # Determina gli indici degli ingredienti richiesti.
    required_indices = []
    for ing in required_ingredients:
        if isinstance(ing, int):
            required_indices.append(ing)
        else:
            try:
                required_indices.append(ingredienti.index(ing))
            except ValueError:
                pass

    total_vars = len(usable_indices)
    base = MAX_QUANTITY + 1
    total_theoretical = base ** total_vars

    print("=== Statistiche Iniziali ===")
    print(f"Ingredienti sbloccati totali: {total_vars}")
    print(f"Ingredienti richiesti: {len(required_indices)}")
    print(f"Combinazioni teoriche: {total_theoretical:,}")
    print("============================\n")
    
    num_workers = 8
    partition_size = total_theoretical // num_workers

    worker_params = []
    for i in range(num_workers):
        start_index = i * partition_size
        end_index = (i + 1) * partition_size if i != num_workers - 1 else total_theoretical
        params = {
            "start_index": start_index,
            "end_index": end_index,
            "variable_indices": usable_indices,
            "required_indices": required_indices,
            "ranges": ranges,
            "worker_id": i
        }
        worker_params.append(params)
    
    start_time = time()
    with Pool(processes=num_workers) as pool:
        results = pool.map(worker_process, worker_params)
    end_time = time()

    best_global_score = -float('inf')
    best_global_quantities = None
    best_global_values = None
    total_stats = {"examined": 0, "skipped_total": 0, "skipped_required": 0, "skipped_range": 0, "valid": 0}
    
    for res in results:
        if res["best_score"] > best_global_score:
            best_global_score = res["best_score"]
            best_global_quantities = res["best_quantities"]
            best_global_values = res["best_values"]
        for key in total_stats:
            total_stats[key] += res["stats"][key]
    
    # Rinomina le chiavi per rispettare quanto aspettato da main.py
    total_stats["examined_combinations"] = total_stats.pop("examined")
    total_stats["valid_combinations"] = total_stats.pop("valid")
    
    total_stats.update({
        "total_combinations": total_theoretical,
        "execution_time": end_time - start_time,
        "best_score": best_global_score if best_global_score > -float('inf') else None
    })
    
    print("\nSearch statistics:")
    print("-" * 30)
    print(f"Total theoretical combinations: {total_theoretical:,}")
    print(f"Examined combinations: {total_stats['examined_combinations']:,}")
    print(f"Skipped for total > 25: {total_stats['skipped_total']:,}")
    print(f"Skipped for missing required ingredients: {total_stats['skipped_required']:,}")
    print(f"Skipped for values out of range: {total_stats['skipped_range']:,}")
    print(f"Valid combinations: {total_stats['valid_combinations']:,}")
    print(f"Execution time: {total_stats['execution_time']:.2f} seconds")
    
    return best_global_quantities, best_global_values, total_stats
