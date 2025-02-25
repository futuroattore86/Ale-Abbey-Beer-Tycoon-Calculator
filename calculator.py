from itertools import product
from time import time

# Coefficienti per ogni ingrediente
coefficients = {
    'gusto': [0.4, 0.8, 1.6, 0.8, 2.0, 1.0, 2.5, -1.0, 0.5, 1.0, 2.0, 1.5, 1.5, 0.5, -0.5, 1.5, 0.3, 1.5, 0.8, 1.2, 1.6, 0.5, 1.0, 1.5, 1.0, 1.0, 1.0, 1.5, -0.5, -1.0, 0.0, 0.5],
    'colore': [0.3, 1.2, 2.0, -0.3, 1.0, 3.0, 0.5, -0.5, 1.0, 0.3, 2.0, 1.0, 1.5, 0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.3, 0.0, 0.0, 2.0, 0.0, 1.0, -1.0, 0.0, -1.0, 0.0, -1.0],
    'gradazione': [1.0, 0.5, 0.0, 0.4, -0.5, -1.0, 0.5, 2.0, 1.5, 1.0, 0.5, 0.5, 0.5, -1.0, 0.0, -1.0, 2.0, 0.5, 0.0, 0.0, 0.0, 0.0, -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.2],
    'schiuma': [0.5, 0.8, 0.0, 2.0, 1.5, 0.5, 0.5, -1.0, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5, 0.0, 0.0, 0.5, 1.0, 0.5, 0.5, 1.0, 0.0, -0.5, 0.0, 0.0, -1.0, -1.0, 0.0, 1.5, 0.0, 0.0, 2.0]
}

# Lista completa degli ingredienti (aggiornata con le traduzioni corrette dal gioco)
ingredienti = [
    'Malto Chiaro',
    'Malto Ambrato',
    'Malto Marrone',
    'Malto di Frumento',
    'Malto di Segale',
    'Malto Tostato',
    'Malto Affumicato',
    'Zucchero',
    'Zucchero Scuro Candito',
    'Miele',
    'Bacche',
    'Uva',
    'Ciliegie',
    'Lievito Standard',
    'Lievito Lager',
    'Lievito Estereo',
    'Lievito Forte',
    'Lievito Selvaggio',
    'Luppolo Classico',
    'Luppolo Cascadus',
    'Luppolo Magnum',
    'Gruit',
    'Eucalipto',
    'Semi di Coriandolo',
    'Scorza di Arancia',
    'Caffè',
    'Pepe',
    'Zucca',
    'Fecola di Frumento',
    'Fiocchi di Mais',
    'Nutrienti per Lievito',
    'Fiocchi di Frumento'
]

# Ordine di sblocco degli ingredienti nel gioco
INGREDIENTI_ORDINE_SBLOCCO = [
    'Malto Chiaro',
    'Lievito Standard',
    'Gruit',
    'Malto Marrone',
    'Malto Ambrato',
    'Luppolo Classico',
    'Miele',
    'Eucalipto',
    'Lievito Forte',
    'Malto di Frumento',
    'Lievito Estereo',
    'Pepe',
    'Zucchero Scuro Candito',
    'Fecola di Frumento',
    'Zucchero',
    'Ciliegie',
    'Bacche',
    'Luppolo Cascadus',
    'Luppolo Magnum',
    'Malto Tostato',
    'Lievito Selvaggio',
    'Lievito Lager',
    'Malto di Segale',
    'Fiocchi di Frumento',
    'Semi di Coriandolo',
    'Scorza di Arancia',
    'Uva',
    'Zucca',
    'Caffè',
    'Fiocchi di Mais',
    'Nutrienti per Lievito',
    'Malto Affumicato'
]

# Ingredienti sempre disponibili all'inizio del gioco
ALWAYS_AVAILABLE = ['Malto Chiaro', 'Lievito Standard']

# Lista degli ingredienti sbloccabili (tutti tranne quelli sempre disponibili)
UNLOCKABLE_INGREDIENTS = [ingr for ingr in INGREDIENTI_ORDINE_SBLOCCO if ingr not in ALWAYS_AVAILABLE]

def calculate_values(quantities):
    """
    Calcola i valori finali di gusto, colore, gradazione e schiuma 
    basati sulle quantità degli ingredienti
    """
    return {
        'gusto': sum(q * c for q, c in zip(quantities, coefficients['gusto'])),
        'colore': sum(q * c for q, c in zip(quantities, coefficients['colore'])),
        'gradazione': sum(q * c for q, c in zip(quantities, coefficients['gradazione'])),
        'schiuma': sum(q * c for q, c in zip(quantities, coefficients['schiuma']))
    }

def calculate_score(values, ranges):
    """
    Calcola un punteggio basato sulla validità dei valori nel range,
    con forte enfasi sui valori alti e sul bilanciamento
    """
    score = 0
    # Pesi modificati per dare più importanza a gusto e gradazione
    weights = {
        'gusto': 1.3,      # Gusto molto importante
        'colore': 0.7,     # Colore meno critico
        'gradazione': 1.2,  # Gradazione molto importante
        'schiuma': 0.8     # Schiuma meno critica
    }
    
    # Teniamo traccia dei valori normalizzati per il calcolo del bilanciamento
    normalized_values = {}
    
    for param in ['gusto', 'colore', 'gradazione', 'schiuma']:
        max_value = ranges[param][1] + 0.99
        
        if ranges[param][0] <= values[param] <= max_value:
            # Bonus base per essere nel range
            score += 8 * weights[param]
            
            # Normalizzazione del valore rispetto al massimo possibile
            normalized_value = values[param] / max_value
            normalized_values[param] = normalized_value
            
            # Bonus progressivo per vicinanza al massimo
            # Più ci si avvicina al massimo, più il bonus cresce esponenzialmente
            proximity_to_max = normalized_value ** 1.5  # Esponente 1.5 per crescita non lineare
            score += proximity_to_max * 10 * weights[param]
            
            # Bonus extra per valori molto alti (90-99% del massimo)
            if 0.90 * max_value <= values[param] <= 0.99 * max_value:
                score += 3 * weights[param]
    
    # Bonus bilanciamento migliorato
    values_list = list(normalized_values.values())
    max_gap = max(values_list) - min(values_list)
    
    # Bonus inversamente proporzionale al gap tra valori
    if max_gap < 0.1:  # Gap minimo (valori molto bilanciati)
        score += 8
    elif max_gap < 0.2:
        score += 6
    elif max_gap < 0.3:
        score += 4
    elif max_gap < 0.4:
        score += 2
    
    # Bonus extra se tutti i valori sono sopra l'80% del loro massimo
    if all(v >= 0.8 for v in normalized_values.values()):
        score += 5
    
    return score

def find_optimal_combination(required_ingredients, ranges, unlocked_ingredients):
    """
    Trova la combinazione ottimale di ingredienti che soddisfa i requisiti
    """
    start_time = time()  # Registra il tempo di inizio
    
    # Debug print per vedere cosa stiamo ricevendo
    print("\nDEBUG INFO:")
    print(f"Ingredienti richiesti: {[ingredienti[i] for i in required_ingredients]}")
    print(f"Ingredienti sbloccati ricevuti: {[ingredienti[i] for i in unlocked_ingredients]}")
    
    # Inizializzazione contatori statistiche
    stats = {
        "examined_combinations": 0,
        "skipped_total": 0,
        "skipped_required": 0,
        "skipped_range": 0,
        "valid_combinations": 0
    }
    
    # Aggiusta i range per considerare i valori arrotondati
    adjusted_ranges = {
        'gusto': [ranges['gusto'][0], ranges['gusto'][1] + 0.99],
        'colore': [ranges['colore'][0], ranges['colore'][1] + 0.99],
        'gradazione': [ranges['gradazione'][0], ranges['gradazione'][1] + 0.99],
        'schiuma': [ranges['schiuma'][0], ranges['schiuma'][1] + 0.99]
    }
    
    # Aggiungi gli indici degli ingredienti sempre disponibili agli sbloccati
    always_available_indices = [ingredienti.index(ingr) for ingr in ALWAYS_AVAILABLE]
    print(f"Ingredienti sempre disponibili: {[ingredienti[i] for i in always_available_indices]}")
    
    # Verifica che gli indici sbloccati siano validi
    valid_unlocked = [i for i in unlocked_ingredients if 0 <= i < len(ingredienti)]
    if len(valid_unlocked) != len(unlocked_ingredients):
        print("ATTENZIONE: Alcuni indici di ingredienti sbloccati non sono validi!")
    
    unlocked_set = set(unlocked_ingredients)
    unlocked_set.update(always_available_indices)
    
    # Crea la lista degli indici degli ingredienti utilizzabili
    usable_indices = sorted(list(unlocked_set))
    print(f"Ingredienti utilizzabili totali: {[ingredienti[i] for i in usable_indices]}")
    print(f"Numero di ingredienti utilizzabili: {len(usable_indices)}")
    
    total_theoretical_combinations = 8**len(usable_indices)
    print(f"\nGenerazione combinazioni per {len(usable_indices)} ingredienti")
    print(f"Combinazioni possibili teoriche: {total_theoretical_combinations:,}")
    
    best_quantities = None
    best_values = None
    best_score = -float('inf')
    
    print("\nRange originali:")
    for param in ranges:
        print(f"{param}: {ranges[param][0]} - {ranges[param][1]}")
    
    print("\nRange adjusted (considerando arrotondamento):")
    for param in adjusted_ranges:
        print(f"{param}: {adjusted_ranges[param][0]} - {adjusted_ranges[param][1]:.2f}")
    
    range_search = range(8)
    # Genera combinazioni solo per gli ingredienti sbloccati
    for partial_quantities in product(range_search, repeat=len(usable_indices)):
        stats["examined_combinations"] += 1
        
        # Crea l'array completo delle quantità
        quantities = [0] * len(ingredienti)
        for idx, qty in zip(usable_indices, partial_quantities):
            quantities[idx] = qty
        
        # Verifica che gli ingredienti richiesti siano presenti
        if not all(quantities[idx] >= 1 for idx in required_ingredients):
            stats["skipped_required"] += 1
            continue
        
        # Verifica il limite totale di unità
        if sum(quantities) > 25:
            stats["skipped_total"] += 1
            continue
        
        values = calculate_values(quantities)
        
        # Usa i range adjusted per la verifica
        if not (adjusted_ranges['gusto'][0] <= values['gusto'] <= adjusted_ranges['gusto'][1] and 
                adjusted_ranges['colore'][0] <= values['colore'] <= adjusted_ranges['colore'][1] and 
                adjusted_ranges['gradazione'][0] <= values['gradazione'] <= adjusted_ranges['gradazione'][1] and 
                adjusted_ranges['schiuma'][0] <= values['schiuma'] <= adjusted_ranges['schiuma'][1]):
            stats["skipped_range"] += 1
            continue
        
        stats["valid_combinations"] += 1
        score = calculate_score(values, ranges)
        if score > best_score:
            best_score = score
            best_quantities = quantities
            best_values = values
            print("\nNuova migliore combinazione trovata:")
            print("Ingredienti utilizzati:")
            for i, qty in enumerate(quantities):
                if qty > 0:
                    print(f"{ingredienti[i]}: {qty}")
            print(f"Valori reali: Gusto={values['gusto']:.2f}, Colore={values['colore']:.2f}, "
                  f"Gradazione={values['gradazione']:.2f}, Schiuma={values['schiuma']:.2f}")
            print(f"Valori visualizzati: Gusto={int(values['gusto'])}, Colore={int(values['colore'])}, "
                  f"Gradazione={int(values['gradazione'])}, Schiuma={int(values['schiuma'])}")
            print(f"Score: {score:.2f}")
    
    end_time = time()
    stats.update({
        "total_combinations": total_theoretical_combinations,
        "execution_time": end_time - start_time,
        "best_score": best_score if best_score > -float('inf') else None
    })
    
    return best_quantities, best_values, stats

def get_ingredient_index(ingredient_name):
    """
    Ottiene l'indice di un ingrediente dal suo nome
    """
    try:
        return ingredienti.index(ingredient_name)
    except ValueError:
        return -1
