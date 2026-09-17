# -*- coding: utf-8 -*-
"""为「全遗物效果.md」主表末尾追加「标签」列。
归类规则：
- 中毒：施加/增强中毒、毒爆相关
- 燃烧：施加/增强燃烧，或火纹石/陨石（燃烧系棋盘引擎）
- 流血：施加流血
- 冰冻：施加寒冷/冰冻，或冰纹石（冰系）
- 闪电：释放/增强闪电、天雷、感电
- 其余（护盾/闪避/反击/暴击/升级/刷新等通用机制）留空
"""
import unicodedata

path = "全遗物效果.md"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

tags = {
    # 闪电
    131: "闪电",   # 引雷器
    132: "闪电",   # 纸封闪电
    133: "闪电",   # 宙斯之眼
    147: "闪电",   # 风暴眼
    162: "闪电",   # 接收天线
    168: "闪电",   # 雷之水晶
    169: "闪电",   # 雷霆剑柄
    170: "闪电",   # 雷神祭品
    175: "闪电",   # 闪电靴
    181: "闪电",   # 感应线圈（感电）
    # 中毒
    134: "中毒",   # 剧毒种子
    135: "中毒",   # 毒液瓶
    138: "中毒",   # 尖嘴口哨
    145: "中毒",   # 榴莲（施加中毒，闪电/暴击仅为触发条件）
    217: "中毒",   # 荆棘铠甲
    231: "中毒",   # 计数器（毒爆）
    232: "中毒",   # 培养皿（毒爆）
    # 燃烧（含火纹石/陨石）
    173: "燃烧",   # 燃烧法阵（火纹石）
    187: "燃烧",   # 熔岩矿脉（火纹石）
    201: "燃烧",   # 夏之叶
    202: "燃烧",   # 打火机
    212: "燃烧",   # 烈焰指环
    214: "燃烧",   # 火焰花
    215: "燃烧",   # 火荆棘
    227: "燃烧",   # 起爆器（火纹石）
    234: "燃烧",   # 小火苗（燃烧→火纹石）
    235: "燃烧",   # 芭蕉扇（火纹石/陨石）
    239: "燃烧",   # 余烬之种（火纹石）
    242: "燃烧",   # 灾祸之种（火纹石/陨石）
    243: "燃烧",   # 不灭之焰
    # 流血
    226: "流血",   # 电锯
    236: "流血",   # 铁锈箭头
    # 冰冻（含寒冷/冰纹石）
    136: "冰冻",   # 冰锥（寒冷增伤）
    174: "冰冻",   # 冰棱盾（寒冷）
    188: "冰冻",   # 凛冬晶核（冰纹石）
    200: "冰冻",   # 冬之叶（寒冷）
    203: "冰冻",   # 冰锥·废弃（寒冷）
    240: "冰冻",   # 寒极之芽（冰纹石）
    # 双标签
    149: "中毒、闪电",  # 分歧处理器：奇数闪电/偶数中毒
    238: "燃烧、冰冻",  # 变色龙：火纹石或冰纹石
}

def disp_width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)

TARGET = 12  # 单元格内容显示宽度（容纳「中毒、闪电」5个全角字符+两侧空格）

def cell(tag):
    content = " " + tag
    pad = TARGET - disp_width(content)
    if pad < 1:
        pad = 1
    return content + " " * pad + "|"

out = []
in_table = False
n_data = n_tagged = 0
seen = set()
for line in lines:
    stripped = line.rstrip("\n")
    if stripped.startswith("| ID"):
        in_table = True
        out.append(stripped + cell("标签") + "\n")
        continue
    if in_table:
        if stripped.startswith("|"):
            rid = stripped.split("|")[1].strip()
            if rid and set(rid) <= set("-: "):
                out.append(stripped + " ------------ |\n")
            else:
                n_data += 1
                try:
                    i = int(rid)
                except ValueError:
                    i = None
                tag = tags.get(i, "") if i is not None else ""
                if i is not None:
                    seen.add(i)
                if tag:
                    n_tagged += 1
                out.append(stripped + cell(tag) + "\n")
        else:
            in_table = False
            out.append(line)
    else:
        out.append(line)

missing = sorted(set(tags) - seen)
with open(path, "w", encoding="utf-8") as f:
    f.writelines(out)

print("data_rows=%d tagged=%d missing_ids=%s" % (n_data, n_tagged, missing))
# 统计各标签数量
from collections import Counter
cnt = Counter()
for t in tags.values():
    for part in t.split("、"):
        cnt[part] += 1
print("tag_counts=%s" % dict(cnt))
