import math
import random

TOTAL_POP = 100
PANJANG_KROMOSOM = 40
BIT_PER_X = 20
BATAS_BAWAH = -10.0
BATAS_ATAS = 10.0
PROB_CROSSOVER = 0.8
PROB_MUTASI = 0.01
MAKS_GENERASI = 500
JUM_ELITE = 2

def decode_biner(kromosom):

    gen_x1 = kromosom[:BIT_PER_X]
    gen_x2 = kromosom[BIT_PER_X:]
    
    desimal_1 = 0
    for b in gen_x1:
        desimal_1 = (desimal_1 * 2) + b
    nilai_x1 = BATAS_BAWAH + (desimal_1 / ((2 ** BIT_PER_X) - 1)) * (BATAS_ATAS - BATAS_BAWAH)

   
    desimal_2 = 0
    for b in gen_x2:
        desimal_2 = (desimal_2 * 2) + b
    nilai_x2 = BATAS_BAWAH + (desimal_2 / ((2 ** BIT_PER_X) - 1)) * (BATAS_ATAS - BATAS_BAWAH)

    return nilai_x1, nilai_x2

def hitung_fungsi_objektif(var_x1, var_x2):
    
    try:
        bagian1 = math.sin(var_x1) * math.cos(var_x2) * math.tan(var_x1 + var_x2)
        bagian2 = 0.5 * math.exp(1 - math.sqrt(var_x2 ** 2))
        
        return -(bagian1 + bagian2)
    except (ValueError, OverflowError, ZeroDivisionError):
       
        return float('inf') 

def bangkitkan_populasi_awal():
    
    pop_awal = []
    for _ in range(TOTAL_POP):
        individu = [random.randint(0, 1) for _ in range(PANJANG_KROMOSOM)]
        pop_awal.append(individu)
    return pop_awal

def seleksi_turnamen(populasi, skor_fitness, ukuran_turnamen=3):
    
    kandidat = random.sample(range(TOTAL_POP), ukuran_turnamen)
    
    pemenang_idx = kandidat[0]
    for idx in kandidat[1:]:
        if skor_fitness[idx] < skor_fitness[pemenang_idx]:
            pemenang_idx = idx
            
    return populasi[pemenang_idx][:]

def pindah_silang(induk1, induk2):
    
    if random.random() <= PROB_CROSSOVER:
        titik_potong = random.randint(1, PANJANG_KROMOSOM - 1)
        anak1 = induk1[:titik_potong] + induk2[titik_potong:]
        anak2 = induk2[:titik_potong] + induk1[titik_potong:]
        return anak1, anak2
    
    return induk1[:], induk2[:]

def mutasi_gen(kromosom):
    
    hasil_mutasi = kromosom[:]
    for i in range(PANJANG_KROMOSOM):
        if random.random() <= PROB_MUTASI:
           
            hasil_mutasi[i] = 1 if hasil_mutasi[i] == 0 else 0
    return hasil_mutasi

def bentuk_generasi_baru(populasi_lama, daftar_fitness):
   
    populasi_baru = []

    
    urutan_terbaik = sorted(range(TOTAL_POP), key=lambda i: daftar_fitness[i])
    for i in range(JUM_ELITE):
        populasi_baru.append(populasi_lama[urutan_terbaik[i]][:])

    
    while len(populasi_baru) < TOTAL_POP:
        ortu1 = seleksi_turnamen(populasi_lama, daftar_fitness)
        ortu2 = seleksi_turnamen(populasi_lama, daftar_fitness)

        keturunan1, keturunan2 = pindah_silang(ortu1, ortu2)

        keturunan1 = mutasi_gen(keturunan1)
        keturunan2 = mutasi_gen(keturunan2)

        populasi_baru.append(keturunan1)
        
        if len(populasi_baru) < TOTAL_POP:
            populasi_baru.append(keturunan2)

    return populasi_baru

def jalankan_algoritma():
    print("-" * 50)
    print(" >>> PROGRAM ALGORITMA GENETIKA (MINIMASI) <<<")
    print("-" * 50)
    print(f" [+] Total Populasi : {TOTAL_POP}")
    print(f" [+] Prob Crossover : {PROB_CROSSOVER}")
    print(f" [+] Prob Mutasi    : {PROB_MUTASI}")
    print(f" [+] Max Generasi   : {MAKS_GENERASI}")
    print("-" * 50)

    populasi_sekarang = bangkitkan_populasi_awal()
    
    kromosom_paling_fit = None
    fitness_paling_baik = float('inf')

    for gen in range(1, MAKS_GENERASI + 1):
        
        
        nilai_fitness = []
        for kromosom in populasi_sekarang:
            x1, x2 = decode_biner(kromosom)
            nilai_fitness.append(hitung_fungsi_objektif(x1, x2))

       
        idx_terbaik_lokal = 0
        for i in range(1, TOTAL_POP):
            if nilai_fitness[i] < nilai_fitness[idx_terbaik_lokal]:
                idx_terbaik_lokal = i

        
        if nilai_fitness[idx_terbaik_lokal] < fitness_paling_baik:
            fitness_paling_baik = nilai_fitness[idx_terbaik_lokal]
            kromosom_paling_fit = populasi_sekarang[idx_terbaik_lokal][:]

        
        if gen == 1 or gen % 50 == 0:
            bx1, bx2 = decode_biner(kromosom_paling_fit)
            print(f" [Gen {gen:>3}] Fitness Terbaik = {fitness_paling_baik:.6f} | x1: {bx1:.5f}, x2: {bx2:.5f}")

       
        populasi_sekarang = bentuk_generasi_baru(populasi_sekarang, nilai_fitness)

    
    print("\n" + "*" * 50)
    print(" KESIMPULAN HASIL PENCARIAN")
    print("*" * 50)
    
    x1_final, x2_final = decode_biner(kromosom_paling_fit)
    teks_kromosom = ''.join(str(bit) for bit in kromosom_paling_fit)
    
    print(" Susunan Genotip (Kromosom Terbaik):")
    print(f" -> Bagian x1 : {teks_kromosom[:BIT_PER_X]}")
    print(f" -> Bagian x2 : {teks_kromosom[BIT_PER_X:]}")
    
    print(f"\n Hasil Dekode Fenotip:")
    print(f" -> Nilai x1  = {x1_final:.7f}")
    print(f" -> Nilai x2  = {x2_final:.7f}")
    
    print(f"\n Nilai Objektif Minimum:")
    print(f" -> f(x1, x2) = {fitness_paling_baik:.7f}")
    print("*" * 50)

if __name__ == "__main__":
   
    random.seed(42) 
    jalankan_algoritma()