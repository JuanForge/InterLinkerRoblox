from concurrent.futures import ThreadPoolExecutor
import zlib
def worker():
    while True:
        data = b"Bonjour" * 1000    
        compressed = zlib.compress(data, level=9)  # level 1-9 (9 = max)    
        decompressed = zlib.decompress(compressed)
        assert decompressed == data


with ThreadPoolExecutor(max_workers=40) as executor:
    futures = [executor.submit(worker) for _ in range(18)]
    for future in futures:
        future.result()