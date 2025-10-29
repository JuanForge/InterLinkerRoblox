import time

N = 1_000_000 * 60
data_list = [f"id_{i}" for i in range(N)]
data_set = set(data_list)

target = "id_1999999"  # dernier élément pour le pire cas


t1 = time.perf_counter()
found1 = target in data_list
t2 = time.perf_counter()


found2 = target in data_set
t3 = time.perf_counter()

print(f"List: {t2 - t1:.6f} sec")
print(f"Set:  {t3 - t2:.6f} sec")
