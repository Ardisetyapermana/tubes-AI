

import math
import random

# ---------------------------------------------------------------
# PARAMETER GA
# ---------------------------------------------------------------
POPULATION_SIZE   = 100      # Ukuran populasi
CHROMOSOME_LENGTH = 40       # 20 bit per variabel (x1 dan x2)
BITS_PER_VAR      = 20       # Resolusi per variabel
X_MIN             = -10.0    # Batas bawah domain
X_MAX             = 10.0     # Batas atas domain
PC                = 0.8      # Probabilitas crossover
PM                = 0.01     # Probabilitas mutasi per bit
MAX_GENERATION    = 500      # Kriteria penghentian: maks generasi
ELITISM_COUNT     = 2        # Jumlah elit yang dipertahankan


# ================================================================
# 1. DEKODE KROMOSOM
# ================================================================
def decode_chromosome(chromosome):
    """
    Kromosom terdiri dari 40 bit: 20 bit pertama = x1, 20 bit berikutnya = x2.
    Rumus dekode: x = x_min + (decimal_value / (2^n - 1)) * (x_max - x_min)
    """
    # Decode x1 (bit 0..19)
    bits_x1 = chromosome[:BITS_PER_VAR]
    decimal_x1 = 0
    for bit in bits_x1:
        decimal_x1 = decimal_x1 * 2 + bit  # konversi biner ke desimal
    x1 = X_MIN + (decimal_x1 / (2 ** BITS_PER_VAR - 1)) * (X_MAX - X_MIN)

    # Decode x2 (bit 20..39)
    bits_x2 = chromosome[BITS_PER_VAR:]
    decimal_x2 = 0
    for bit in bits_x2:
        decimal_x2 = decimal_x2 * 2 + bit
    x2 = X_MIN + (decimal_x2 / (2 ** BITS_PER_VAR - 1)) * (X_MAX - X_MIN)

    return x1, x2


# ================================================================
# 2. FUNGSI OBJEKTIF & FITNESS
# ================================================================
def objective_function(x1, x2):
    """
    f(x1, x2) = -(sin(x1)*cos(x2)*tan(x1+x2) + 0.5*exp(1 - sqrt(x2^2)))
    Tujuan: MINIMASI f  →  kita ingin f sekecil mungkin (nilai negatif besar).
    """
    try:
        term1 = math.sin(x1) * math.cos(x2) * math.tan(x1 + x2)
        term2 = 0.5 * math.exp(1 - math.sqrt(x2 ** 2))
        return -(term1 + term2)
    except (ValueError, OverflowError, ZeroDivisionError):
        # Jika tan undefined atau overflow, kembalikan nilai buruk (besar)
        return float('inf')


def calculate_fitness(chromosome):
    """
    Fitness = nilai objektif (karena kita meminimalkan,
    kromosom dengan f lebih kecil = lebih baik).
    Untuk seleksi tournament/roulette kita konversi ke fitness positif:
      fitness = 1 / (1 + f - f_min)  → dilakukan di fungsi seleksi.
    Di sini kembalikan nilai f langsung (lebih kecil = lebih baik).
    """
    x1, x2 = decode_chromosome(chromosome)
    return objective_function(x1, x2)


# ================================================================
# 3. INISIALISASI POPULASI
# ================================================================
def initialize_population():
    """
    Membuat populasi awal secara acak.
    Setiap kromosom adalah list berisi 40 bit (0 atau 1).
    """
    population = []
    for _ in range(POPULATION_SIZE):
        # Setiap bit dipilih acak 0 atau 1
        chromosome = [random.randint(0, 1) for _ in range(CHROMOSOME_LENGTH)]
        population.append(chromosome)
    return population


# ================================================================
# 4. PEMILIHAN ORANGTUA — Tournament Selection
# ================================================================
def tournament_selection(population, fitness_values, tournament_size=3):
    """
    Tournament Selection:
    - Pilih 'tournament_size' individu secara acak.
    - Kembalikan individu dengan fitness terbaik (nilai f terkecil).
    """
    selected_indices = [random.randint(0, POPULATION_SIZE - 1)
                        for _ in range(tournament_size)]
    # Pilih indeks dengan nilai fitness terkecil (minimasi)
    best_index = selected_indices[0]
    for idx in selected_indices[1:]:
        if fitness_values[idx] < fitness_values[best_index]:
            best_index = idx
    return population[best_index][:]   # kembalikan salinan kromosom


# ================================================================
# 5. CROSSOVER — Single-Point Crossover
# ================================================================
def crossover(parent1, parent2):
    """
    Single-Point Crossover:
    - Pilih satu titik potong secara acak.
    - Tukar segmen setelah titik potong antara kedua orangtua.
    - Crossover hanya terjadi jika angka acak < PC.
    """
    if random.random() < PC:
        point = random.randint(1, CHROMOSOME_LENGTH - 1)  # titik potong
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
    else:
        # Tidak crossover → anak = salinan orangtua
        child1 = parent1[:]
        child2 = parent2[:]
    return child1, child2


# ================================================================
# 6. MUTASI — Bit-Flip Mutation
# ================================================================
def mutate(chromosome):
    """
    Bit-Flip Mutation:
    - Setiap bit diflip (0→1 atau 1→0) dengan probabilitas PM.
    """
    mutated = chromosome[:]
    for i in range(CHROMOSOME_LENGTH):
        if random.random() < PM:
            mutated[i] = 1 - mutated[i]   # flip bit
    return mutated


# ================================================================
# 7. PERGANTIAN GENERASI — Elitism + Generational Replacement
# ================================================================
def create_next_generation(population, fitness_values):
    """
    Pergantian generasi dengan strategi Elitisme:
    - Simpan ELITISM_COUNT individu terbaik langsung ke generasi baru.
    - Sisa slot diisi oleh offspring hasil seleksi, crossover, dan mutasi.
    """
    new_population = []

    # --- Elitisme: pertahankan individu terbaik ---
    sorted_indices = sorted(range(POPULATION_SIZE),
                            key=lambda i: fitness_values[i])
    for i in range(ELITISM_COUNT):
        new_population.append(population[sorted_indices[i]][:])

    # --- Isi sisa populasi dengan offspring ---
    while len(new_population) < POPULATION_SIZE:
        # Pilih dua orangtua via tournament selection
        parent1 = tournament_selection(population, fitness_values)
        parent2 = tournament_selection(population, fitness_values)

        # Crossover
        child1, child2 = crossover(parent1, parent2)

        # Mutasi
        child1 = mutate(child1)
        child2 = mutate(child2)

        new_population.append(child1)
        if len(new_population) < POPULATION_SIZE:
            new_population.append(child2)

    return new_population


# ================================================================
# 8. MAIN — LOOP EVOLUSI
# ================================================================
def run_genetic_algorithm():
    """
    Loop utama Genetic Algorithm.
    Kriteria penghentian: sudah mencapai MAX_GENERATION generasi.
    """
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

    # --- Inisialisasi populasi awal ---
    population = initialize_population()

    best_chromosome_ever = None
    best_fitness_ever    = float('inf')

    # --- Loop evolusi ---
    for generation in range(1, MAX_GENERATION + 1):

        # Hitung fitness seluruh populasi
        fitness_values = [calculate_fitness(chrom) for chrom in population]

        # Temukan individu terbaik di generasi ini
        best_idx = 0
        for i in range(1, POPULATION_SIZE):
            if fitness_values[i] < fitness_values[best_idx]:
                best_idx = i

        # Update best ever
        if fitness_values[best_idx] < best_fitness_ever:
            best_fitness_ever    = fitness_values[best_idx]
            best_chromosome_ever = population[best_idx][:]

        # Cetak progres setiap 50 generasi
        if generation % 50 == 0 or generation == 1:
            bx1, bx2 = decode_chromosome(best_chromosome_ever)
            print(f"  Gen {generation:>4} | Best f = {best_fitness_ever:12.6f} "
                  f"| x1 = {bx1:8.5f}, x2 = {bx2:8.5f}")

        # Buat generasi baru
        population = create_next_generation(population, fitness_values)

    # --- Hasil akhir ---
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


# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    random.seed(42)   # seed untuk reproduksibilitas hasil
    run_genetic_algorithm()