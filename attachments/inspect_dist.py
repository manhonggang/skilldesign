import numpy as np, math
M = 20

def Z_of_sigma(s, M):
    k = np.arange(0, M)
    return np.sum(np.exp(-k*k/(2*s*s)))

def sigma_for_peak(p, M):
    target = 1.0/p; lo, hi = 1e-3, 100.0
    for _ in range(200):
        mid=(lo+hi)*0.5
        if Z_of_sigma(mid,M) < target: lo=mid
        else: hi=mid
    return (lo+hi)*0.5

def dist(M, N, p):
    s = sigma_for_peak(p, M)
    k = np.arange(0, M)
    w = np.exp(-k*k/(2*s*s))[::-1]
    P = w/w.sum()
    return s, P

for N, p in [(10, 0.80), (5, 0.467), (1, 0.20)]:
    s, P = dist(M, N, p)
    print(f"\n=== N={N}  p_target={p:.3f}  sigma={s:.4f} ===")
    cum = 0
    for d in range(M, 0, -1):
        pr = P[d-1]
        cum += pr
        if pr < 1e-5 and d < M-2:
            print(f"  d={d:2d}: {pr*100:8.5f}%   (累计 {cum*100:.3f}%)  <- 后续基本为 0")
            break
        print(f"  d={d:2d}: {pr*100:8.4f}%   (累计 {cum*100:.3f}%)")
