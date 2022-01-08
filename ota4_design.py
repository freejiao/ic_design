# 将ota1 design做成一个函数
# 反复迭代
import re  # 字符串相关
import os  # to exec hspice
import math
import gc
import sys

BASE2_DIR = ('D:\synopsys\ota2')
sys.path.append(BASE2_DIR)
import pyspice_tool as pst
import ota_tool as otd  # ota design

# os.system('source /cad/synopsys/hspice/hspice/bin/cshrc.meta')
# 用户约束
wtail_init = 5e-6
rz_init = 0.1
rz_step = 20  # 定义rz迭代的步长
gaint = 5000 * 1.05
idt = 10e-3
GBW = 300e6
cur2 = 7e-3
gain2 = 30
fnd = GBW * 1.5 * 1.05 * 1.14
cout_s1 = 2e-12 * 1  # 表示s1的输出寄生电容，默认为0，求解一遍后迭代重新设计s2
cmil = 3e-12
cl = 5e-12
vcmi = 1.1
vcmo = 0.9
pst.cir_modify('stage2_pz.sp', 25, rz_init)  # 将Rz初值清零
pst.cir_modify('stage2_pz.sp', 27, 0.1)  # 将S1的VB接上去
pst.cir_modify('stage2_pz.sp', 28, wtail_init)  # 将尾管的W设为默认的5u
[state, gm_cgg, gm_cgg_min, gain2_real, cur_s2, c2_par, cc_par] = \
    otd.ota2_design_pre(cur2, gain2, fnd, cout_s1, cmil, cl, vcmi, vcmo)
# 增加Cmil的原则，给定增益后，从0.2CL开始迭代，百分之五向上递增Cmil

gain1 = gaint / gain2
# cur1 = idt - id_target
cur1 = idt - cur_s2
cload1 = gain2 * (cmil + cc_par) + c2_par
gbw1 = GBW / gain2 * 1.14  # 单看第一级的GBW，是整体GBW除以第二级增益
lmax = 10e-6
l_step = 0.2e-6  # L的步长为0.5u
c1_par_last = 1
c1_par = 0.5
while c1_par < c1_par_last:
    c1_par_last = c1_par
    [vp0_new, ln_new, lp_new, wn_new, wp_new, gbw_new, gain_new, gmi_new, itotal_new, c1_par] = \
        otd.ota1_design(cur1, gain1, gbw1, cload1, vcmi, lmax)
    if c1_par < c1_par_last:
        vp0 = vp0_new
        ln = ln_new
        lp = lp_new
        wn = wn_new
        wp = wp_new
        gbw_s1 = gbw_new
        gain_s1 = gain_new
        cur_s1 = itotal_new
        gm_s1 = gmi_new
    if ln - l_step > 1e-6:
        lmax = ln - l_step
    else:
        break

pst.cir_modify('stage2_pz.sp', 30, ln)
pst.cir_modify('stage2_pz.sp', 31, lp)
pst.cir_modify('stage2_pz.sp', 32, wn)
pst.cir_modify('stage2_pz.sp', 33, wp)
pst.cir_modify('stage2_pz.sp', 34, vp0)

os.system('hspice stage2_pz.sp -o stage2_pz.lis')
gbw_final = pst.getResu('stage2_pz.ma0', 'gbw')
phase_margin = pst.getResu('stage2_pz.ma0', 'pm')
ac_gain = pst.getResu('stage2_pz.ma0', 'ac_gain')
print("phase margin is %.4g , gbw is %.4g , ac_gain is %.4g ." % (phase_margin, gbw_final, ac_gain))

# 修改尾管结构后扫描Rz的过程
id_tail = pst.getResu('stage2_pz.ms0', 'id_tail')  # 当前电流
id_s1 = pst.getResu('stage2_pz.ms0', 'id_s1')  # 当前s1需要的电流
wtail = wtail_init * id_s1 / id_tail
pst.cir_modify('stage2_pz.sp', 28, wtail)
pst.cir_modify('stage2_pz.sp', 27, 1e12)  # 将尾部的电压偏置关调

# 迭代rz
os.system('hspice stage2_pz.sp -o stage2_pz.lis')
gbw_final = pst.getResu('stage2_pz.ma0', 'gbw')
phase_margin = pst.getResu('stage2_pz.ma0', 'pm')
gm_s2 = pst.getResu('stage2_pz.ms0', 'gm_s2')
rz = 1 / gm_s2
pst.cir_modify('stage2_pz.sp', 25, rz)
os.system('hspice stage2_pz.sp -o stage2_pz.lis')

while pst.getResu('stage2_pz.ma0', 'pm') < 60 or \
      pst.getResu('stage2_pz.ma0', 'gbw') < GBW:  # 两个条件同时约束
    rz += rz_step
    pst.cir_modify('stage2_pz.sp', 25, rz)
    os.system('hspice stage2_pz.sp -o stage2_pz.lis')
    pm = pst.getResu('stage2_pz.ma0', 'pm')
    gbw = pst.getResu('stage2_pz.ma0', 'gbw')


os.system('hspice stage2_pz.sp -o stage2_pz.lis')
gbw_final = pst.getResu('stage2_pz.ma0', 'gbw')
phase_margin = pst.getResu('stage2_pz.ma0', 'pm')

pst.getPole('stage2_pz.lis', 'poles.txt')
pst.getZero('stage2_pz.lis', 'zeros.txt')
gc.collect()  # 垃圾回收
