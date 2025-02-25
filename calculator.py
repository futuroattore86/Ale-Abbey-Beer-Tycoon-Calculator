from itertools import product

# Coefficienti per ogni ingrediente
coefficients = {
    'gusto': [0.4, 0.8, 1.6, 0.8, 2.0, 1.0, 2.5, -1.0, 0.5, 1.0, 2.0, 1.5, 1.5, 0.5, -0.5, 1.5, 0.3, 1.5, 0.8, 1.2, 1.6, 0.5, 1.0, 1.5, 1.0, 1.0, 1.0, 1.5, -0.5, -1.0, 0.0, 0.5],
    'colore': [0.3, 1.2, 2.0, -0.3, 1.0, 3.0, 0.5, -0.5, 1.0, 0.3, 2.0, 1.0, 1.5, 0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.3, 0.0, 0.0, 2.0, 0.0, 1.0, -1.0, 0.0, -1.0, 0.0, -1.0],
    'gradazione': [1.0, 0.5, 0.0, 0.4, -0.5, -1.0, 0.5, 2.0, 1.5, 1.0, 0.5, 0.5, 0.5, -1.0, 0.0, -1.0, 2.0, 0.5, 0.0, 0.0, 0.0, 0.0, -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.2],
    'schiuma': [0.5, 0.8, 0.0, 2.0, 1.5, 0.5, 0.5, -1.0, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5, 0.0, 0.0, 0.5, 1.0, 0.5, 0.5, 1.0, 0.0, -0.5, 0.0, 0.0, -1.0, -1.0, 0.0, 1.5, 0.0, 0.0, 2.0]
}

# Lista completa degli ingredienti
ingredienti = [
    'Malto chiaro',
    'Malto ambrato',
    'Malto marrone',
    'Malto di frumento',
    'Malto di segale',
    'Malto tostato',
    'Malto affumicato',
    'Zucchero',
    'Zucchero di canna caramellato',
    'Miele',
    'Bacche',
    'Uva',
    'Ciliegie',
    'Lievito standard',
    'Lievito Lager',
    'Lievito Esterico',
    'Lievito forte',
    'Lievito selvatico',
    'Luppolo classico',
    'Luppolo Cascade',
    'Luppolo Magnum',
    'Gruit',
    'Eucalipto',
    'Semi di coriandolo',
    'Scorza d\'arancia',
    'Caffè',
    'Pepe',
    'Zucca',
    'Amido di frumento',
    'Corn Flakes',
    'Nutrienti per lievito',
    'Frumento non maltato'
]

# Ingredienti sempre disponibili all'inizio del gioco
ALWAYS_AVAILABLE = ['Malto chiaro', 'Lievito standard']

# Lista degli ingredienti sbloccabili (tutti tranne quelli sempre disponibili)
UNLOCKABLE_INGREDIENTS = [ingr for ingr in ingredienti if ingr not in ALWAYS_AVAILABLE]

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
    # Aggiusta i range per considerare i valori arrotondati
    adjusted_ranges = {
        'gusto': [ranges['gusto'][0], ranges['gusto'][1] + 0.99],
        'colore': [ranges['colore'][0], ranges['colore'][1] + 0.99],
        'gradazione': [ranges['gradazione'][0], ranges['gradazione'][1] + 0.99],
        'schiuma': [ranges['schiuma'][0], ranges['schiuma'][1] + 0.99]
    }
    
    # Aggiungi gli indici degli ingredienti sempre disponibili agli sbloccati
    always_available_indices = [ingredienti.index(ingr) for ingr in ALWAYS_AVAILABLE]
    unlocked_set = set(unlocked_ingredients)
    unlocked_set.update(always_available_indices)
    
    # Crea la lista degli indici degli ingredienti utilizzabili
    usable_indices = sorted(list(unlocked_set))
    
    best_quantities = None
    best_values = None
    best_score = -float('inf')
    counter = 0

    print("\nRange originali:")
    for param in ranges:
        print(f"{param}: {ranges[param][0]} - {ranges[param][1]}")
    
    print("\nRange adjusted (considerando arrotondamento):")
    for param in adjusted_ranges:
        print(f"{param}: {adjusted_ranges[param][0]} - {adjusted_ranges[param][1]:.2f}")

    range_search = range(6)
    # Genera combinazioni solo per gli ingredienti sbloccati
    for partial_quantities in product(range_search, repeat=len(usable_indices)):
        counter += 1
        
        # Crea l'array completo delle quantità
        quantities = [0] * len(ingredienti)
        for idx, qty in zip(usable_indices, partial_quantities):
            quantities[idx] = qty
            
        # Verifica che gli ingredienti richiesti siano presenti
        if not all(quantities[idx] >= 1 for idx in required_ingredients):
            continue
            
        # Verifica il limite totale di unità
        if sum(quantities) > 25:
            continue
            
        values = calculate_values(quantities)
        
        # Usa i range adjusted per la verifica
        if (adjusted_ranges['gusto'][0] <= values['gusto'] <= adjusted_ranges['gusto'][1] and 
            adjusted_ranges['colore'][0] <= values['colore'] <= adjusted_ranges['colore'][1] and 
            adjusted_ranges['gradazione'][0] <= values['gradazione'] <= adjusted_ranges['gradazione'][1] and 
            adjusted_ranges['schiuma'][0] <= values['schiuma'] <= adjusted_ranges['schiuma'][1]):
            
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

    return best_quantities, best_values, counter

def get_ingredient_index(ingredient_name):
    """
    Ottiene l'indice di un ingrediente dal suo nome
    """
    try:
        return ingredienti.index(ingredient_name)
    except ValueError:
        return -1
