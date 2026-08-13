"""
自动训练天数分布设计  (M=50, N_max=20)
- 锚点: N=1 -> 20%,  N=20 -> 80%  线性插值, 截断
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
matplotlib.rcParams["axes.unicode_minus"] = False

M = 50
N_MAX = 20
P_LO, P_HI = 0.20, 0.80

def peak_target(N):
    p = P_LO + (P_HI - P_LO) * (N - 1) / (N_MAX - 1)
    return float(np.clip(p, P_LO, P_HI))

def Z_of_sigma(s, M):
    k = np.arange(0, M)
    return np.sum(np.exp(-k*k/(2*s*s)))

def sigma_for_peak(p, M, lo=1e-3, hi=200.0):
    target = 1.0/p
    for _ in range(200):
        mid=(lo+hi)*0.5
        if Z_of_sigma(mid,M) < target: lo=mid
        else: hi=mid
    return (lo+hi)*0.5

def dist(M, sigma):
    """P[0]->d=1 ... P[M-1]->d=M(峰值)"""
    k = np.arange(0, M)
    w = np.exp(-k*k/(2*sigma*sigma))[::-1]
    return w/w.sum()

N_list = [1, 5, 10, 15, 20]
results=[]
for N in N_list:
    p = peak_target(N)
    s = sigma_for_peak(p, M)
    P = dist(M, s)
    results.append((N,p,s,P))
    print(f"N={N:2d}  p={p:.3f}  sigma={s:.4f}  P(M)={P[-1]:.4f}  sum={P.sum():.4f}")

fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), gridspec_kw={"width_ratios":[1.5,1]})

ax = axes[0]
days = np.arange(1, M+1)
colors = ["#9aa0a6", "#5b9bd5", "#70ad47", "#ffc000", "#c00000"]
for (N,p,s,P), c in zip(results, colors):
    ax.plot(days, P, "-o", color=c, ms=3, lw=1.6,
            label=f"N={N}  (σ={s:.2f}, 峰值={P[-1]*100:.0f}%)")
    ax.annotate(f"{P[-1]*100:.0f}%", xy=(M, P[-1]),
                xytext=(6,2), textcoords="offset points",
                color=c, fontsize=9, fontweight="bold")
ax.axvline(M, color="#7f7f7f", ls="--", lw=1, label=f"玩家最大天数 M={M}")
ax.set_xlabel("自动训练到达天数 d")
ax.set_ylabel("P(d)")
ax.set_title(f"自动训练天数分布 (半正态, 中心=M={M})")
ax.set_xticks(np.arange(0, M+1, 5))
ax.grid(alpha=0.25)
ax.legend(fontsize=9, loc="upper left")

ax = axes[1]
Ns = np.arange(1, N_MAX+1)
peaks = [peak_target(N) for N in Ns]
ax.plot(Ns, peaks, "-o", color="#c00000", lw=2, ms=5)
for N, p in zip(Ns[::2], peaks[::2]):
    ax.annotate(f"{p*100:.0f}%", (N,p), xytext=(0,8),
                textcoords="offset points", ha="center", fontsize=8)
ax.set_xlabel("自动训练次数 N")
ax.set_ylabel("峰值概率 P(M)")
ax.set_title(f"峰值概率随训练次数提升 (N_max={N_MAX})")
ax.set_xticks(Ns)
ax.set_ylim(0,1.0)
ax.grid(alpha=0.25)

plt.tight_layout()
out = "D:/Al/技能设计/attachments/auto_train_dist_M50_N20.png"
plt.savefig(out, dpi=140, bbox_inches="tight")
print("saved:", out)

# 逐天检查 N=20 时分布
print("\n=== N=20 (M=50) 分布尾部 ===")
N,p,s,P = results[-1]
cum=0
for d in range(M, 0, -1):
    pr = P[d-1]; cum += pr
    if pr < 1e-5 and d < M-3:
        print(f"  d={d:2d}: {pr*100:8.5f}% (累计 {cum*100:.3f}%)  <- 后续≈0")
        break
    print(f"  d={d:2d}: {pr*100:8.4f}% (累计 {cum*100:.3f}%)")
