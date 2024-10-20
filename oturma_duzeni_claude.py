import pandas as pd
import numpy as np
from collections import Counter

def distribute_participants(csv_file, num_tables):
    # CSV dosyasını okuyun
    df = pd.read_csv(csv_file, sep=';')
    
    # Katılımcıları karıştırın
    df = df.sample(frac=1, random_state=123456).reset_index(drop=True)

    # Her masaya atanacak katılımcı sayısını hesaplayın
    participants_per_table = len(df) // num_tables
    extra_participants = len(df) % num_tables
    
    # Masaları hazırlayın
    tables = [[] for _ in range(num_tables)]
    
    # BRANŞ, İLÇE ve OKUL için sayaçlar oluşturun
    branch_counters = [Counter() for _ in range(num_tables)]
    district_counters = [Counter() for _ in range(num_tables)]
    school_counters = [Counter() for _ in range(num_tables)]
    
    for _, participant in df.iterrows():
        # En uygun masayı bulun
        best_table = min(range(num_tables), key=lambda i: (
            len(tables[i]),
            branch_counters[i][participant['BRANŞ']],
            district_counters[i][participant['İLÇE']],
            school_counters[i][participant['OKUL']]
        ))
        
        # Katılımcıyı en uygun masaya ekleyin
        tables[best_table].append(participant.to_dict())
        branch_counters[best_table][participant['BRANŞ']] += 1
        district_counters[best_table][participant['İLÇE']] += 1
        school_counters[best_table][participant['OKUL']] += 1
    
    # Sonuçları DataFrame'lere dönüştürün
    table_dfs = [pd.DataFrame(table) for table in tables]
    
    return table_dfs

def print_table_stats(table_dfs):
    for i, df in enumerate(table_dfs):
        print(f"Masa {i+1}:")
        print(f"  Katılımcı sayısı: {len(df)}")
        print(f"  Benzersiz BRANŞ sayısı: {df['BRANŞ'].nunique()}")
        print(f"  Benzersiz İLÇE sayısı: {df['İLÇE'].nunique()}")
        print(f"  Benzersiz OKUL sayısı: {df['OKUL'].nunique()}")
        print()

# Kullanım örneği
csv_file = './OKA Katılımcılar_w_name.csv'  # CSV dosyanızın adını buraya girin
num_tables = 7 # İstediğiniz masa sayısını buraya girin

table_dfs = distribute_participants(csv_file, num_tables)
print_table_stats(table_dfs)

# İsterseniz, sonuçları ayrı CSV dosyalarına kaydedebilirsiniz
for i, df in enumerate(table_dfs):
    df.to_csv(f'masa_{i+1}.csv', index=False, sep=';', encoding='utf-8-sig')