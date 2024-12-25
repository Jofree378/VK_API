import time
from tqdm import tqdm

pbar = tqdm(["a", "b", "c", "d"], ncols=80, colour='green')

for char in pbar:
    pbar.set_description(f"Processing '{char}'")