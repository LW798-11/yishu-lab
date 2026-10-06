"""复算《易数实验室》的全部数学结论。

运行：python verify_math.py
输出 all checks passed 即全部通过。
"""

from fractions import Fraction
from itertools import product
from collections import Counter

# ---------------------------------------------------------------
# 1. 两种起卦法的一爻概率（精确分数）
#    统一写法：取值 = 9 - (A + B + C)，A、B、C 为独立 0-1 随机变量
# ---------------------------------------------------------------

def dist(p_a):
    """P(A=1) = p_a，B、C 公平。返回 {取值: 概率}。"""
    out = {v: Fraction(0) for v in (6, 7, 8, 9)}
    for a, pa in ((0, 1 - p_a), (1, p_a)):
        for b, pb in ((0, Fraction(1, 2)), (1, Fraction(1, 2))):
            for c, pc in ((0, Fraction(1, 2)), (1, Fraction(1, 2))):
                out[9 - (a + b + c)] += pa * pb * pc
    return out

coin = dist(Fraction(1, 2))
yarrow = dist(Fraction(1, 4))

assert coin == {6: Fraction(1, 8), 7: Fraction(3, 8), 8: Fraction(3, 8), 9: Fraction(1, 8)}, coin
assert yarrow == {6: Fraction(1, 16), 7: Fraction(5, 16), 8: Fraction(7, 16), 9: Fraction(3, 16)}, yarrow

# 阳概率 = P(7) + P(9)；变概率 = P(6) + P(9)；两种方法都应为 1/2 与 1/4
for d in (coin, yarrow):
    assert d[7] + d[9] == Fraction(1, 2)
    assert d[6] + d[9] == Fraction(1, 4)

# 条件概率：P(阳爻变 | 阳) 与 P(阴爻变 | 阴)
# 铜钱法对称（均 1/4）；大衍法不对称（3/8 vs 1/8，三倍关系）
assert coin[9] / (coin[7] + coin[9]) == Fraction(1, 4)
assert coin[6] / (coin[6] + coin[8]) == Fraction(1, 4)
assert yarrow[9] / (yarrow[7] + yarrow[9]) == Fraction(3, 8)
assert yarrow[6] / (yarrow[6] + yarrow[8]) == Fraction(1, 8)

# ---------------------------------------------------------------
# 2. 克莱因四元群 {恒等, 错, 综, 错∘综} 在 64 卦上的轨道数
#    Burnside：轨道数 = (64 + fix(错) + fix(综) + fix(错∘综)) / 4
#    fix(错) = 0（按位取反无不动点）
#    fix(综)  = 回文卦 = 2^3 = 8
#    fix(错综) = 反回文卦 = 2^3 = 8
# ---------------------------------------------------------------
assert (64 + 0 + 8 + 8) // 4 == 20

def cuo(x):
    return x ^ 0b111111

def zong(x):
    return int("{:06b}".format(x)[::-1], 2)

seen = set()
orbit_sizes = []
for x in range(64):
    if x in seen:
        continue
    orb = {x, cuo(x), zong(x), cuo(zong(x))}
    orbit_sizes.append(len(orb))
    seen |= orb
assert len(orbit_sizes) == 20, len(orbit_sizes)
assert sorted(Counter(orbit_sizes).items()) == [(2, 8), (4, 12)]

# ---------------------------------------------------------------
# 3. 互卦：F₂ 上的线性映射，秩 4，像 16，每像恰 4 个原像
# ---------------------------------------------------------------
def hu(x):
    b = [(x >> i) & 1 for i in range(6)]
    o = [b[1], b[2], b[3], b[2], b[3], b[4]]  # 下互 = 爻(2,3,4)，上互 = 爻(3,4,5)
    return sum(bit << i for i, bit in enumerate(o))

fibers = Counter(hu(x) for x in range(64))
assert len(fibers) == 16                      # 像的大小 = 2^秩
assert set(fibers.values()) == {4}            # 每像 4 个原像 → 4 对 1 满射，不可逆

# ---------------------------------------------------------------
# 4. 伏羲（先天）卦序，邵雍原序：序号 = bitrev6(63 - 值) + 1
# ---------------------------------------------------------------
def bitrev6(v):
    return int("{:06b}".format(v)[::-1], 2)

def xiantian(value):
    return bitrev6(63 - value) + 1

# 八卦三爻（自下而上，阳 = 1）
QIAN, DUI, LI, ZHEN, XUN, KAN, GEN, KUN = 0b111, 0b011, 0b101, 0b001, 0b110, 0b010, 0b100, 0b000

def value(upper, lower):
    return lower | (upper << 3)

assert xiantian(value(QIAN, QIAN)) == 1      # 乾为天
assert xiantian(value(DUI, QIAN)) == 2      # 泽天夬
assert xiantian(value(LI, QIAN)) == 3       # 火天大有
assert xiantian(value(KUN, QIAN)) == 8      # 地天泰
assert xiantian(value(QIAN, DUI)) == 9      # 天泽履
assert xiantian(value(KUN, ZHEN)) == 32     # 地雷复
assert xiantian(value(QIAN, XUN)) == 33     # 天风姤
assert xiantian(value(QIAN, KUN)) == 57     # 天地否
assert xiantian(value(GEN, GEN)) == 55      # 艮为山
assert xiantian(value(KUN, GEN)) == 56      # 山地剥
assert xiantian(value(KUN, KUN)) == 64      # 坤为地

# ---------------------------------------------------------------
# 5. 数字取模起卦（梅花易数式约定）的自洽性
#    N mod 8 定上卦、⌊N/8⌋ mod 8 定下卦（余 0 记 8）、N mod 6 定动爻（余 0 记第 6 爻）
# ---------------------------------------------------------------
NUM = {1: QIAN, 2: DUI, 3: LI, 4: ZHEN, 5: XUN, 6: KAN, 7: GEN, 8: KUN}

def cast_number(n):
    upper = NUM[((n % 8) + 8) % 8 or 8]
    lower = NUM[((n // 8 % 8) + 8) % 8 or 8]
    moving = ((n % 6) + 6) % 6 or 6       # 1..6
    return upper, lower, moving

# 64 个卦都应能被某个 N 取到，且动爻分布均匀（每个位置 1/6）
reached = set()
moving_count = Counter()
for n in range(1, 64 * 6 + 1):
    u, l, m = cast_number(n)
    reached.add(value(u, l))
    moving_count[m] += 1
assert len(reached) == 64
assert len(set(moving_count.values())) == 1

print("all checks passed")
