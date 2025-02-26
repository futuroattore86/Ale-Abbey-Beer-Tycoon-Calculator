from itertools import product
from time import time

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

def calculate_values_incremental(base_values, ingredient_idx, quantity_delta):
    """
    Calcola i valori in modo incrementale aggiungendo o rimuovendo un ingrediente
    """
    return {
        'gusto': base_values['gusto'] + quantity_delta * coefficients['gusto'][ingredient_idx],
        'colore': base_values['colore'] + quantity_delta * coefficients['colore'][ingredient_idx],
        'gradazione': base_values['gradazione'] + quantity_delta * coefficients['gradazione'][ingredient_idx],
        'schiuma': base_values['schiuma'] + quantity_delta * coefficients['schiuma'][ingredient_idx]
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
    Calcola un punteggio basato sulla somma dei valori all'interno dei range richiesti.
    Se un valore è fuori range, il punteggio viene fortemente penalizzato.
    """
    score = 0
    
    for param in ['gusto', 'colore', 'gradazione', 'schiuma']:
        min_value = ranges[param][0]
        max_value = ranges[param][1]
        current_value = values[param]
        
        if min_value <= current_value <= max_value:
            # Se il valore è nel range, il punteggio aumenta proporzionalmente al valore
            score += current_value
        else:
            # Se il valore è fuori range, penalizza fortemente
            score -= 1000
    
    return score
def find_optimal_combination(required_ingredients, ranges, unlocked_ingredients):
    """
    Trova la combinazione ottimale di ingredienti che soddisfa i requisiti
    utilizzando ottimizzazioni per il calcolo incrementale e early termination
    """
    start_time = time()
    
    print("\nDEBUG INFO:")
    print(f"Ingredienti richiesti: {[ingredienti[i] for i in required_ingredients]}")
    print(f"Ingredienti sbloccati ricevuti: {[ingredienti[i] for i in unlocked_ingredients]}")
    
    stats = {
        "examined_combinations": 0,
        "skipped_total": 0,
        "skipped_required": 0,
        "skipped_range": 0,
        "valid_combinations": 0
    }
    
    # Aggiusta i range per considerare i valori arrotondati
    adjusted_ranges = {
        'gusto': [ranges['gusto'][0], ranges['gusto'][1]],
        'colore': [ranges['colore'][0], ranges['colore'][1]],
        'gradazione': [ranges['gradazione'][0], ranges['gradazione'][1]],
        'schiuma': [ranges['schiuma'][0], ranges['schiuma'][1]]
    }
    
    # Aggiungi gli indici degli ingredienti sempre disponibili
    always_available_indices = [ingredienti.index(ingr) for ingr in ALWAYS_AVAILABLE]
    unlocked_set = set(unlocked_ingredients)
    unlocked_set.update(always_available_indices)
    usable_indices = sorted(list(unlocked_set))
    
    # Prepara la base con gli ingredienti obbligatori
    base_quantities = [0] * len(ingredienti)
    for req_idx in required_ingredients:
        base_quantities[req_idx] = 1
    
    # Calcola i valori base una sola volta
    base_values = calculate_base_values(base_quantities)
    
    # Prepara gli ingredienti variabili
    variable_indices = [idx for idx in usable_indices if idx not in required_ingredients]
    total_theoretical_combinations = 10**len(variable_indices)  # range 0-9
    
    print(f"\nGenerazione combinazioni per {len(variable_indices)} ingredienti variabili")
    print(f"Combinazioni possibili teoriche: {total_theoretical_combinations:,}")
    
    best_quantities = None
    best_values = None
    best_score = -float('inf')
    range_search = range(10)  # 0-9 unità
    
    def is_in_range(values):
        """Verifica se i valori sono nei range consentiti"""
        return (adjusted_ranges['gusto'][0] <= values['gusto'] <= adjusted_ranges['gusto'][1] and 
                adjusted_ranges['colore'][0] <= values['colore'] <= adjusted_ranges['colore'][1] and 
                adjusted_ranges['gradazione'][0] <= values['gradazione'] <= adjusted_ranges['gradazione'][1] and 
                adjusted_ranges['schiuma'][0] <= values['schiuma'] <= adjusted_ranges['schiuma'][1])

    def generate_combinations(partial, current_sum, position, current_values):
        """
        Genera combinazioni in modo ricorsivo con early termination e calcolo incrementale
        """
        nonlocal best_score, best_quantities, best_values
        
        if current_sum > 25:
            stats["skipped_total"] += 1
            return
            
        if position == len(variable_indices):
            stats["examined_combinations"] += 1
            
            if not is_in_range(current_values):
                stats["skipped_range"] += 1
                return
                
            stats["valid_combinations"] += 1
            score = calculate_score(current_values, ranges)
            
            if score > best_score:
                best_score = score
                quantities = base_quantities.copy()
                for idx, qty in zip(variable_indices, partial):
                    quantities[idx] = qty
                best_quantities = quantities
                best_values = current_values.copy()
                
                print("\nNuova migliore combinazione trovata:")
                print("Ingredienti utilizzati:")
                for i, qty in enumerate(quantities):
                    if qty > 0:
                        print(f"{ingredienti[i]}: {qty}")
                print(f"Valori reali: Gusto={current_values['gusto']:.2f}, "
                      f"Colore={current_values['colore']:.2f}, "
                      f"Gradazione={current_values['gradazione']:.2f}, "
                      f"Schiuma={current_values['schiuma']:.2f}")
                print(f"Score: {score:.2f}")
            return
            
        for qty in range_search:
            # Calcolo incrementale dei valori
            new_values = calculate_values_incremental(
                current_values,
                variable_indices[position],
                qty
            )
            generate_combinations(
                partial + [qty],
                current_sum + qty,
                position + 1,
                new_values
            )

    # Avvia la generazione ricorsiva con i valori base
    generate_combinations([], sum(base_quantities), 0, base_values)
    
    end_time = time()
    stats.update({
        "total_combinations": total_theoretical_combinations,
        "execution_time": end_time - start_time,
        "best_score": best_score if best_score > -float('inf') else None
    })
    
    print("\nStatistiche della ricerca:")
    print("-" * 30)
    print(f"Combinazioni teoriche: {stats['total_combinations']:,}")
    print(f"Combinazioni esaminate: {stats['examined_combinations']:,}")
    print(f"Scartate per limite totale > 25: {stats['skipped_total']:,}")
    print(f"Scartate per ingredienti obbligatori: {stats['skipped_required']:,}")
    print(f"Scartate per valori fuori range: {stats['skipped_range']:,}")
    print(f"Combinazioni valide: {stats['valid_combinations']:,}")
    print(f"\nTempo di esecuzione: {stats['execution_time']:.2f} secondi")
    
    return best_quantities, best_values, stats

def get_ingredient_index(ingredient_name):
    """
    Ottiene l'indice di un ingrediente dal suo nome
    """
    try:
        return ingredienti.index(ingredient_name)
    except ValueError:
        return -1
