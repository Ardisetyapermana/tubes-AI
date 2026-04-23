

import math
import random


POPULATION_SIZE   = 100      
CHROMOSOME_LENGTH = 40       
BITS_PER_VAR      = 20       
X_MIN             = -10.0   
X_MAX             = 10.0     
PC                = 0.8      
PM                = 0.01    
MAX_GENERATION    = 500      
ELITISM_COUNT     = 2        


def decode_chromosome(chromosome):
    
    bits_x1 = chromosome[:BITS_PER_VAR]
    decimal_x1 = 0
    for bit in bits_x1:
        decimal_x1 = decimal_x1 * 2 + bit  
    x1 = X_MIN + (decimal_x1 / (2 ** BITS_PER_VAR - 1)) * (X_MAX - X_MIN)

    bits_x2 = chromosome[BITS_PER_VAR:]
    decimal_x2 = 0
    for bit in bits_x2:
        decimal_x2 = decimal_x2 * 2 + bit
    x2 = X_MIN + (decimal_x2 / (2 ** BITS_PER_VAR - 1)) * (X_MAX - X_MIN)

    return x1, x2



def objective_function(x1, x2):
    
    
    
    try:
        term1 = math.sin(x1) * math.cos(x2) * math.tan(x1 + x2)
        term2 = 0.5 * math.exp(1 - math.sqrt(x2 ** 2))
        return -(term1 + term2)
    except (ValueError, OverflowError, ZeroDivisionError):
        
        return float('inf')


def calculate_fitness(chromosome):
   

    x1, x2 = decode_chromosome(chromosome)
    return objective_function(x1, x2)

def initialize_population():
   
    population = []
    for _ in range(POPULATION_SIZE):
        
        chromosome = [random.randint(0, 1) for _ in range(CHROMOSOME_LENGTH)]
        population.append(chromosome)
    return population

def tournament_selection(population, fitness_values, tournament_size=3):
   
    selected_indices = [random.randint(0, POPULATION_SIZE - 1)
                        for _ in range(tournament_size)]
    
    best_index = selected_indices[0]
    for idx in selected_indices[1:]:
        if fitness_values[idx] < fitness_values[best_index]:
            best_index = idx
    return population[best_index][:]   

def crossover(parent1, parent2):
    
    if random.random() < PC:
        point = random.randint(1, CHROMOSOME_LENGTH - 1)  
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
    else:

        child1 = parent1[:]
        child2 = parent2[:]
    return child1, child2

def mutate(chromosome):
    
    mutated = chromosome[:]
    for i in range(CHROMOSOME_LENGTH):
        if random.random() < PM:
            mutated[i] = 1 - mutated[i]   # flip bit
    return mutated

def create_next_generation(population, fitness_values):
   
    new_population = []

    sorted_indices = sorted(range(POPULATION_SIZE),
                            key=lambda i: fitness_values[i])
    for i in range(ELITISM_COUNT):
        new_population.append(population[sorted_indices[i]][:])

    while len(new_population) < POPULATION_SIZE:
        
        parent1 = tournament_selection(population, fitness_values)
        parent2 = tournament_selection(population, fitness_values)

        
        child1, child2 = crossover(parent1, parent2)

        
        child1 = mutate(child1)
        child2 = mutate(child2)

        new_population.append(child1)
        if len(new_population) < POPULATION_SIZE:
            new_population.append(child2)

    return new_population

def run_genetic_algorithm():
    
    print("=" * 60)
    print("  GENETIC ALGORITHM — Minimasi f(x1, x2)")
    print("=" * 60)
    print(f"  Ukuran Populasi : {POPULATION_SIZE}")
    print(f"  Panjang Kromosom: {CHROMOSOME_LENGTH} bit ({BITS_PER_VAR} bit/variabel)")
    print(f"  Pc (Crossover)  : {PC}")
    print(f"  Pm (Mutasi)     : {PM}")
    print(f"  Max Generasi    : {MAX_GENERATION}")
    print(f"  Elitisme        : {ELITISM_COUNT} individu")
    print("=" * 60)

    population = initialize_population()

    best_chromosome_ever = None
    best_fitness_ever    = float('inf')

    for generation in range(1, MAX_GENERATION + 1):

        fitness_values = [calculate_fitness(chrom) for chrom in population]

        best_idx = 0
        for i in range(1, POPULATION_SIZE):
            if fitness_values[i] < fitness_values[best_idx]:
                best_idx = i

        
        if fitness_values[best_idx] < best_fitness_ever:
            best_fitness_ever    = fitness_values[best_idx]
            best_chromosome_ever = population[best_idx][:]

        
        if generation % 50 == 0 or generation == 1:
            bx1, bx2 = decode_chromosome(best_chromosome_ever)
            print(f"  Gen {generation:>4} | Best f = {best_fitness_ever:12.6f} "
                  f"| x1 = {bx1:8.5f}, x2 = {bx2:8.5f}")

        population = create_next_generation(population, fitness_values)


    print("\n" + "=" * 60)
    print("  HASIL AKHIR")
    print("=" * 60)
    x1_best, x2_best = decode_chromosome(best_chromosome_ever)

    print(f"\n  Kromosom Terbaik:")
    bits_str = ''.join(map(str, best_chromosome_ever))
    print(f"    x1 (bit 0-19) : {bits_str[:BITS_PER_VAR]}")
    print(f"    x2 (bit 20-39): {bits_str[BITS_PER_VAR:]}")
    print(f"    Full          : {bits_str}")

    print(f"\n  Nilai Dekode:")
    print(f"    x1 = {x1_best:.6f}")
    print(f"    x2 = {x2_best:.6f}")
    print(f"\n  Nilai Fungsi Minimum:")
    print(f"    f(x1, x2) = {best_fitness_ever:.6f}")
    print("=" * 60)

    return best_chromosome_ever, x1_best, x2_best, best_fitness_ever


if __name__ == "__main__":
    random.seed(42)   
    run_genetic_algorithm()