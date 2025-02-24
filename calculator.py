from itertools import product

# Coefficienti per ogni ingrediente
coefficients = {
    'gusto': [0.4, 0.8, 1, 0.5, 0.5, 1, 1.6, 0.8, 0.8, 0.3],
    'colore': [0.3, 1.2, 0.3, -0.3, 0, 0, 2, 0, -0.3, 0],
    'gradazione': [1, 0.5, 1, 0, -1, -0.2, 0, 0, 0.4, 2],
    'schiuma': [0.5, 0.8, 0, 0, -0.5, -0.5, 0, 0.5, 2, 0.5]
}

ingredienti = [
    'Malto chiaro',
    'Malto ambrato',
    'Miele',
    'Gruit',
    'Lievito standard',
    'Eucalipto',
    'Malto marrone',
    'Luppolo classico',
    'Malto di frumento',
    'Lievito forte'
]

# Funzione per calcolare i valori dati i coefficienti e le quantità di ingredienti
def calculate_values(quantities):
    return {
        'gusto': sum(q * c for q, c in zip(quantities, coefficients['gusto'])),
        'colore': sum(q * c for q, c in zip(quantities, coefficients['colore'])),
        'gradazione': sum(q * c for q, c in zip(quantities, coefficients['gradazione'])),
        'schiuma': sum(q * c for q, c in zip(quantities, coefficients['schiuma']))
    }

# Funzione per calcolare la "distanza" dai limiti superiori dei range
def calculate_score(values, ranges):
    score = 0
    score += (values['gusto'] - ranges['gusto'][0]) / (ranges['gusto'][1] - ranges['gusto'][0])
    score += (values['colore'] - ranges['colore'][0]) / (ranges['colore'][1] - ranges['colore'][0])
    score += (values['gradazione'] - ranges['gradazione'][0]) / (ranges['gradazione'][1] - ranges['gradazione'][0])
    score += (values['schiuma'] - ranges['schiuma'][0]) / (ranges['schiuma'][1] - ranges['schiuma'][0])
    return score

# Funzione principale per trovare la combinazione ottimale di ingredienti
def find_optimal_combination(required_ingredients, ranges):
    range_search = range(6)
    best_quantities = None
    best_values = None
    best_score = -float('inf')
    counter = 0

    for quantities in product(range_search, repeat=10):
        counter += 1
        if all(quantities[idx] >= 1 for idx in required_ingredients) and sum(quantities) <= 25:
            values = calculate_values(quantities)
            if (ranges['gusto'][0] <= values['gusto'] <= ranges['gusto'][1] and 
                ranges['colore'][0] <= values['colore'] <= ranges['colore'][1] and 
                ranges['gradazione'][0] <= values['gradazione'] <= ranges['gradazione'][1] and 
                ranges['schiuma'][0] <= values['schiuma'] <= ranges['schiuma'][1]):
                score = calculate_score(values, ranges)
                if score > best_score:
                    best_score = score
                    best_quantities = quantities
                    best_values = values

    return best_quantities, best_values, counter