"""
自动训练天数分布设计
- 横轴: 训练天数 d (1..M)
- 纵轴: 落在该天数的概率 P(d)
- 正态分布中心 = M (玩家最远训练天数)
- 截掉右侧 (d > M), 保留左半
- 随自动训练次数 N 增大, 峰值 P(M) 增大
- 约束: N=1 -> P(M)=0.20 ; N=10 -> P(M)=0.80
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
matplotlib.rcParams["axes.unicode_minus"] = False

M = 20  # 玩家最大训练天数

def peak_target(N):
    """N=1 -> 0.20, N=10 -> 0.80 线性插值, 两侧截断"""
    p = 0.20 + (0.80 - 0.20) * (N - 1) / (10 - 1)
    return float(np.clip(p, 0.20, 0.80))

def Z_of_sigma(sigma, M):
    k = np.arange(0, M)  # k = M - d, k=0..M-1
    return np.sum(np.exp(-k*k / (2*sigma*sigma)))

def sigma_for_peak(p_target, M, lo=1e-3, hi=100.0):
    """二分法求 sigma 使得 1/Z = p_target  <=>  Z = 1/p_target"""
    target_Z = 1.0 / p_target
    for _ in range(200):
        mid = (lo + hi) * 0.5
        Z = Z_of_sigma(mid, M)
        if Z < target_Z:        # sigma 太小, 集中度太高 -> 需要更大 sigma
            lo = mid
        else:
            hi = mid
    return (lo + hi) * 0.5

def dist(M, sigma):
    """返回 P[d-1], 即 P[0]对应 d=1, P[M-1]对应 d=M (峰值)"""
    k = np.arange(0, M)        # k = M - d, k=0 -> d=M (峰值)
    w = np.exp(-k*k / (2*sigma*sigma))[::-1]  # 反转使索引 = d-1
    return w / w.sum()

# ---- 计算 ----
N_list = [1, 2, 3, 5, 10]
results = []
for N in N_list:
    p = peak_target(N)
    s = sigma_for_peak(p, M)
    P = dist(M, s)
    results.append((N, p, s, P))
    print(f"N={N:2d}  peak_target={p:.3f}  sigma={s:.4f}  P(M)={P[-1]:.4f}  sum={P.sum():.4f}")

# ---- 画图: 左图分布, 右图 peak-N 曲线 ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios":[1.4, 1]})

ax = axes[0]
days = np.arange(1, M+1)
colors = ["#9aa0a6", "#5b9bd5", "#70ad47", "#ffc000", "#c00000"]
for (N, p, s, P), c in zip(results, colors):
    ax.plot(days, P, "-o", color=c, ms=4, lw=1.6,
            label=f"N={N}  (σ={s:.2f}, 峰值={P[-1]*100:.0f}%)")
    ax.annotate(f"{P[-1]*100:.0f}%",
                xy=(M, P[-1]), xytext=(6, 2), textcoords="offset points",
                color=c, fontsize=9, fontweight="bold")
ax.axvline(M, color="#7f7f7f", ls="--", lw=1, label=f"玩家最大天数 M={M}")
ax.set_xlabel("自动训练到达天数 d")
ax.set_ylabel("P(d)")
ax.set_title(f"自动训练天数分布 (半正态, 中心=M={M})")
ax.set_xticks(np.arange(0, M+1, 2))
ax.grid(alpha=0.25)
ax.legend(fontsize=9, loc="upper left")

ax = axes[1]
Ns = np.arange(1, 11)
peaks = [peak_target(N) for N in Ns]
ax.plot(Ns, peaks, "-o", color="#c00000", lw=2, ms=6)
for N, p in zip(Ns, peaks):
    ax.annotate(f"{p*100:.0f}%", (N, p), textcoords="offset points",
                xytext=(0, 8), ha="center", fontsize=8)
ax.set_xlabel("自动训练次数 N")
ax.set_ylabel("峰值概率 P(M)")
ax.set_title("峰值概率随训练次数提升")
ax.set_xticks(Ns)
ax.set_ylim(0, 1.0)
ax.grid(alpha=0.25)

plt.tight_layout()
out = "D:/Al/技能设计/attachments/auto_train_dist.png"
plt.savefig(out, dpi=140, bbox_inches="tight")
print("saved:", out)
