import torch
import time

device = "cuda" if torch.cuda.is_available() else "cpu"

x = torch.rand(10000, 10000).to(device)

start = time.time()
y = torch.matmul(x, x)
print("Time:", time.time() - start)
print("Device:", device)