# ota tool，在pyspice_tool的基础上集成某些电路函数的设计函数
import re  # 字符串相关
import os  # to exec hspice
import math
import gc
import sys

import numpy as np

BASE2_DIR = ('D:\synopsys\ota2')
sys.path.append(BASE2_DIR)
import pyspice_tool as pst


def ota1_design(itotal, gain0, GBW0, CL, VCMO, l_sweep):
    # 输入5个参数，返回mark标志与电路参数
    # 展望：
    # mark=1代表成功且符合要求，mark=2代表经过迭代，但是最终没达到指标
    # mark=3代表第一次迭代就崩了。
    # 如果给的电流太大导致设计出来的GBW偏高，迭代一次，降低所有管子的w，
    # 因此需要返回最终的电流值
    # w尺寸太大时需要将w折断成多个m

    # 系统设定
    SUPPLY = 1.8
    initial_width = 600e-9
    unit_length = 5e-9
    unit_vp0 = 20e-3  # 以20mV的间距调整尾端电压，加至vin-vp-vth<-100即停止
    initial_length = 180e-9
    vp0 = 0
    vcmi = 0.9
    vgt0 = 0.3  # 这个值用来第一把仿真时确定一个使输入管工作在vgt=300mV下的尾端电压
    vregion3 = 0.15  # 定义亚阈值深度
    gmid_step = 1
    gain_margin = 0.01  # 百分之一的增益裕度
    # l_sweep = 5e-6
    l_sweep2 = l_sweep * 1.1  # 先按照l_sweep的设定扫描，扫描之后更改W会导致无解，所以调高阈值继续扫描

    # start!!!!!
    gbw_rad = GBW0 * 6.18
    gmid_min = gbw_rad * CL * 1.05 / (itotal / 2)
    wn = initial_width
    wp = initial_width
    ln = initial_length
    # 先设置默认的W/L尺寸，得到vth，反标两个VP电压

    pst.cir_modify('input.sp', 10, CL)  # 第十行是负载电容
    pst.cir_modify('input.sp', 11, SUPPLY)
    pst.cir_modify('mos.sp', 15, SUPPLY)
    pst.cir_modify('mos.sp', 10, wn)
    pst.cir_modify('mos.sp', 11, wp)
    pst.cir_modify('mos.sp', 7, ln)
    pst.cir_modify('mos.sp', 9, ln)
    pst.cir_modify('mos.sp', 14, VCMO)
    pst.cir_modify('mos.sp', 16, vp0)
    pst.cir_modify('mos.sp', 17, l_sweep)  # 预设L上限
    os.system('hspice mos.sp')
    vth = pst.getResu('mos.ms0', 'vthn')
    if vcmi - vth > vgt0:
        vp0 = vcmi - vth - vgt0
    else:
        vp0 = 0

    gbw_past = 0
    stop_all_signal = 0
    gmid_coeff = 1
    optim = 0  # 为0代表没有被优化过，用以增益判断失败和gmid判断失败时可以反标上次结果
    iter_times = 0

    while stop_all_signal == 0:
        # 迭代部分的参数更新，主要保留vp0之前的结果
        gmid_min = gmid_min * gmid_coeff
        wn = initial_width
        wp = initial_width
        ln = initial_length
        # 这里把尺寸复原，保险一点
        pst.cir_modify('mos.sp', 10, wn)
        pst.cir_modify('mos.sp', 11, wp)
        pst.cir_modify('mos.sp', 7, ln)
        pst.cir_modify('mos.sp', 9, ln)
        pst.cir_modify('mos.sp', 16, vp0)  # 保持300mV的初始值

        # 第一次求解使得增益满足条件的NMOS的L值
        pst.cir_modify('mos.sp', 6, gain0 * 2 * (1 + gain_margin))  # Jiao puts the gain para at line 6
        os.system('hspice mos.sp')
        while pst.getResu('mos.ms0', 'lengn') == 'failed':
            iter_times += 1
            vp0 += unit_vp0
            if vcmi - vp0 - vth < -vregion3:  # 说明vgs已经比vth小100mV了，不再尝试
                if optim == 0:  # 说明第一把就失败了
                    print("cannot find a proper size to satisfy gain")
                    sys.exit()
                else:  # 说明已经有上次的结果了
                    stop_signal = 1
                    stop_all_signal = 1
                    wn = wn_last
                    wp = wp_last
                    ln = ln_last
                    lp = lp_last
                    vp0 = vp0_last
                    pst.cir_modify('input.sp', 12, vp0)
                    pst.real_modify(ln, lp, wn, wp, 'input.sp')
                    os.system('hspice input.sp')
                    gbw = pst.getResu('input.ma0', 'gbw')
                    dc_gain = pst.getResu('input.ma0', 'gain')
                    gmi = pst.getResu('input.ms0', 'gm')
                    itotal = pst.getResu('input.ms0', 'id')
                    print("After iteration, no gain solution... So this is the best results that can be achieved...")
                    break
            pst.cir_modify('mos.sp', 16, vp0)
            os.system('hspice mos.sp')
        if stop_all_signal == 1:  # 辅助跳出多层循环
            break

        ln = pst.getResu('mos.ms0', 'lengn')
        ln_num = math.ceil(ln / unit_length)
        ln = ln_num * unit_length
        pst.cir_modify('mos.sp', 7, ln)  # Jiao puts the LNP para at line 7
        pst.cir_modify('mos.sp', 9, ln)  # Only LNP is modified,the gain and routid don't change!

        stop_signal = 0
        while stop_signal == 0:
            iter_times += 1
            os.system('hspice mos.sp')
            gmid = pst.getResu('mos.ms0', 'gm_id')
            vth = pst.getResu('mos.ms0', 'vthn')
            if gmid > gmid_min:  # 如果此时的gm/id大于设定的最小值满足要求
                stop_signal = 1
                ln = pst.getResu('mos.ms0', 'lengn')
                ln_num = math.ceil(ln / unit_length)
                ln = ln_num * unit_length
                pst.cir_modify('mos.sp', 7, ln)
                pst.cir_modify('mos.sp', 9, ln)
                os.system('hspice mos.sp')
            else:
                vp0 = vp0 + unit_vp0
                if vcmi - vp0 - vth < -vregion3:  # 说明vgs已经比vth小100mV了，不再尝试
                    if optim == 0:  # 说明第一把就失败了
                        print("cannot find a proper size to satisfy gbw and power!")
                        sys.exit()
                    else:  # 说明已经有上次的结果了
                        stop_signal = 1
                        stop_all_signal = 1
                        wn = wn_last
                        wp = wp_last
                        ln = ln_last
                        lp = lp_last
                        vp0 = vp0_last
                        pst.cir_modify('input.sp', 12, vp0)
                        pst.real_modify(ln, lp, wn, wp, 'input.sp')
                        os.system('hspice input.sp')
                        gbw = pst.getResu('input.ma0', 'gbw')
                        dc_gain = pst.getResu('input.ma0', 'gain')
                        gmi = pst.getResu('input.ms0', 'gm')
                        itotal = pst.getResu('input.ms0', 'id')
                        print(
                            "After iteration, no gm/id solution... So this is the best results that can be achieved...")
                        break
                else:
                    pst.cir_modify('mos.sp', 16, vp0)
        if stop_all_signal == 1:  # 辅助跳出多层循环
            break

        # 大规模迭代，求出合适的N管和P管尺寸
        # 求N管尺寸
        idn = pst.getResu('mos.ms0', 'idn')
        wn = wn * itotal / idn
        pst.cir_modify('mos.sp', 17, l_sweep2)
        pst.cir_modify('mos.sp', 10, wn)
        os.system('hspice mos.sp')
        ln = pst.getResu('mos.ms0', 'lengn')
        ln = unit_length * math.ceil(ln / unit_length)
        pst.cir_modify('mos.sp', 7, ln)
        pst.cir_modify('mos.sp', 9, ln)
        os.system('hspice mos.sp')
        idn = pst.getResu('mos.ms0', 'idn')
        wn = wn * itotal / idn
        pst.cir_modify('mos.sp', 10, wn)
        os.system('hspice mos.sp')
        idn = pst.getResu('mos.ms0', 'idn')
        nroutid = pst.getResu('mos.ms0', 'nroutid')

        # 开算P管尺寸
        pst.cir_modify('mos.sp', 8, nroutid)
        os.system('hspice mos.sp')
        lp = pst.getResu('mos.ms0', 'lengp')
        if lp == 'failed':  # 如果失败 最大的可能就是P管最小的尺寸增益也比这个大
            lp = 180e-9
        else:
            lp = unit_length * math.ceil(lp / unit_length)
        pst.cir_modify('mos.sp', 7, lp)  # Jiao puts the LNP para at line 7
        pst.cir_modify('mos.sp', 9, lp)  # LNP和LNP0参数一起调节
        os.system('hspice mos.sp')
        idp = pst.getResu('mos.ms0', 'idp')
        wp = wp * idn / idp  # N管电流已经标定下来了
        pst.cir_modify('mos.sp', 11, wp)
        os.system('hspice mos.sp')  # 代入WP，再求一遍P管尺寸
        lp = pst.getResu('mos.ms0', 'lengp')
        if lp == 'failed':  # 如果失败 最大的可能就是P管最小的尺寸增益也比这个大
            lp = 180e-9
        else:
            lp = unit_length * math.ceil(lp / unit_length)
        pst.cir_modify('mos.sp', 7, lp)  # Jiao puts the LNP para at line 7
        pst.cir_modify('mos.sp', 9, lp)  # LNP和LNP0参数一起调节
        os.system('hspice mos.sp')  # 更新一遍P管L，重算电流
        idp = pst.getResu('mos.ms0', 'idp')
        wp = wp * idn / idp  # N管电流已经标定下来了
        pst.cir_modify('mos.sp', 11, wp)

        # 最终写入input.sp
        pst.cir_modify('input.sp', 12, vp0)  # input.sp中， 12行是修vp的
        pst.real_modify(ln, lp, wn, wp, 'input.sp')
        os.system('hspice input.sp')
        gbw = pst.getResu('input.ma0', 'gbw')
        dc_gain = pst.getResu('input.ma0', 'gain')
        gmi = pst.getResu('input.ms0', 'gm')
        itotal = pst.getResu('input.ms0', 'id')
        optim = 1  # 到这已经确定是优化过了
        if gbw >= GBW0:  # 这里得到的gbw已经是Hz了，因为sp文件中是dec扫描的
            stop_all_signal = 1
        else:
            if gbw < gbw_past:  # 说明更新之后反而变小了，已经不能再长管子尺寸了，将上一次的结果反标回去，仿真一把收工
                stop_all_signal = 1
                wn = wn_last
                wp = wp_last
                ln = ln_last
                lp = lp_last
                vp0 = vp0_last
                pst.cir_modify('input.sp', 12, vp0)
                pst.real_modify(ln, lp, wn, wp, 'input.sp')
                os.system('hspice input.sp')
                gbw = pst.getResu('input.ma0', 'gbw')
                dc_gain = pst.getResu('input.ma0', 'gain')
                gmi = pst.getResu('input.ms0', 'gm')
                itotal = pst.getResu('input.ms0', 'id')
                print("After iteration, worse results... So this is the best results that can be achieved...")
            else:
                vp0_last = vp0
                wn_last = wn
                wp_last = wp
                ln_last = ln
                lp_last = lp
                gbw_past = gbw
                gmid_coeff = 1 + (GBW0 / gbw - 1) * gmid_step

    # 弄好之后仿真gbw，如果最终带宽高于目标带宽就多次缩放
    os.system('hspice input.sp')
    gbw = pst.getResu('input.ma0', 'gbw')
    if gbw > GBW0 * 1.05:
        wp = wp / (gbw / GBW0)
        wn = wn / (gbw / GBW0)
        pst.real_modify(ln, lp, wn, wp, 'input.sp')
        os.system('hspice input.sp')
        itotal = pst.getResu('input.ms0', 'id')
        gbw = pst.getResu('input.ma0', 'gbw')
        dc_gain = pst.getResu('input.ma0', 'gain')
        gmi = pst.getResu('input.ms0', 'gm')
    if gbw > GBW0 * 1.05:
        wp = wp / (gbw / GBW0)
        wn = wn / (gbw / GBW0)
        pst.real_modify(ln, lp, wn, wp, 'input.sp')
        os.system('hspice input.sp')
        itotal = pst.getResu('input.ms0', 'id')
        gbw = pst.getResu('input.ma0', 'gbw')
        dc_gain = pst.getResu('input.ma0', 'gain')
        gmi = pst.getResu('input.ms0', 'gm')
    if gbw > GBW0 * 1.05:
        wp = wp / (gbw / GBW0)
        wn = wn / (gbw / GBW0)
        pst.real_modify(ln, lp, wn, wp, 'input.sp')
        os.system('hspice input.sp')
        itotal = pst.getResu('input.ms0', 'id')
        gbw = pst.getResu('input.ma0', 'gbw')
        dc_gain = pst.getResu('input.ma0', 'gain')
        gmi = pst.getResu('input.ms0', 'gm')
    if gbw > GBW0 * 1.05:
        wp = wp / (gbw / GBW0)
        wn = wn / (gbw / GBW0)
        pst.real_modify(ln, lp, wn, wp, 'input.sp')
        os.system('hspice input.sp')
        itotal = pst.getResu('input.ms0', 'id')
        gbw = pst.getResu('input.ma0', 'gbw')
        dc_gain = pst.getResu('input.ma0', 'gain')
        gmi = pst.getResu('input.ms0', 'gm')
    # 迭代三次尺寸, 再仿真一次获取输出端总电容
    os.system('hspice input.sp')
    cout_par = pst.getResu('input.ms0', 'cddn') + pst.getResu('input.ms0', 'cddp')
    return vp0, ln, lp, wn, wp, gbw, dc_gain, gmi, itotal, cout_par


def ota2_design_pre(itotal, gain0, fnd, cpar_in, cmil, cl, vcmi, vcmo):
    # 输入参数为总电流，第二级增益，非主极点频率(函数外算好并留出百分之五的裕度)，
    # 第一级产生的寄生值cpar_in，密勒值，负载电容值，第二级输出直流，第二级输出直流
    # 理想公式为gm/cl*1/(1+cgg/cmil)=fnd*6.18，假设设计很不合理，导致最终符合条件时cgg=1/2cmil，
    # 此时gm=fnd*6.18*cl*1.5，gm/cgg=fnd*6.18*cl*1.5*2/cmil，增益算好之后立马判断此时的gm/cgg是否大于这个值
    # 如果不满足，返回一个mark，然后调低增益/增大密勒来试验；
    # 如果满足，令k=gm/cgg，则求出此时需要的gm值，并对比此时的gm/id计算需要的总id，如果满足要求，继续设计。

    ## 返回值预定义
    state_flag = 0
    # 状态标志，为0是啥事没有，为1是gm/cgs无法满足fnd=1.5GBW的需求，为2是能满足fnd，但是电流太大
    id_target = 0
    cg_par = 0  # 栅极带来的寄生电容，返回给第一级用

    ## 关键参数定义
    unit_length = 5e-9
    initial_width = 5e-6  # 第二级的初始宽度都定为5u，后续根据P、N管的电流比调整N管的宽度
    initial_length = 180e-9
    initial_finger = 1

    ## 主函数
    pst.cir_modify('stage2_pz.sp', 24, initial_finger)
    pst.cir_modify('stage2_pz.sp', 23, vcmi)
    pst.cir_modify('stage2_pz.sp', 21, cmil)
    pst.cir_modify('stage2_pz.sp', 20, cl)
    pst.cir_modify('stage2_pz.sp', 18, vcmo)
    pst.cir_modify('stage2_pz.sp', 14, gain0 * 2)
    pst.cir_modify('stage2_pz.sp', 11, initial_length)
    pst.cir_modify('stage2_pz.sp', 12, initial_length)  # 清零l尺寸
    pst.cir_modify('stage2_pz.sp', 8, initial_width)
    pst.cir_modify('stage2_pz.sp', 10, initial_width)
    os.system('hspice stage2_pz.sp')
    gain_pre = pst.getResu('stage2_pz.ms0', 'gain_pre')  # 获取P管的最小本征增益
    if gain_pre > gain0 * 2:  # 说明增益没法再低了
        lp = initial_length  # 这里还要做一个返回参数来报告最小增益
    else:  # 否则，取出L值，修改网表，重新仿真
        lp = pst.getResu('stage2_pz.ms0', 'lengp')
        if lp == 'failed':  # 如果失败 最大的可能就是P管最小的尺寸增益也比这个大
            lp = 180e-9
        else:
            lp = unit_length * math.ceil(lp / unit_length)
        pst.cir_modify('stage2_pz.sp', 11, lp)
        pst.cir_modify('stage2_pz.sp', 12, lp)
        os.system('hspice stage2_pz.sp')

    gain_pre = pst.getResu('stage2_pz.ms0', 'gain_pre') / 2
    gm0 = pst.getResu('stage2_pz.ms0', 'gm0')
    idp0 = pst.getResu('stage2_pz.ms0', 'idp0')
    proutid = pst.getResu('stage2_pz.ms0', 'proutid')
    pst.cir_modify('stage2_pz.sp', 13, proutid)
    os.system('hspice stage2_pz.sp')
    ln = pst.getResu('stage2_pz.ms0', 'lengn')
    if ln == 'failed':  # 如果失败 最大的可能就是N管最小的尺寸增益也比这个大
        ln = 180e-9
    else:
        ln = unit_length * math.ceil(ln / unit_length)
    pst.cir_modify('stage2_pz.sp', 11, ln)
    pst.cir_modify('stage2_pz.sp', 12, ln)
    os.system('hspice stage2_pz.sp')
    idn0 = pst.getResu('stage2_pz.ms0', 'idn0')
    wn = initial_width / (idn0 / idp0)
    pst.cir_modify('stage2_pz.sp', 10, wn)
    pst.cir_modify('stage2_pz.sp', 7, lp)
    pst.cir_modify('stage2_pz.sp', 9, ln)
    os.system('hspice stage2_pz.sp')  # 初步找到所有的S2尺寸，开始读取寄生电容
    cgg2 = pst.getResu('stage2_pz.ms0', 'cggp')
    ccx = pst.getResu('stage2_pz.ms0', 'ccx')
    clx = pst.getResu('stage2_pz.ms0', 'clx')

    # 开始计算
    #    if gm0 / cgg2 < gm_cgg_min:  # cgg最大都可以是cmil了，所以gm0/cgg2如果比这个还小，不能接受
    #        state_flag = 1
    #        return state_flag, 0, 0, 0, id_target, 0
    #    else:
    # 之所以去掉上述代码，是因为这里根本不care “cgg应该是多少”，只要最终输出的电流满足要求，就是合理的

    k = cgg2 / gm0
    m = ccx / gm0
    n = clx / gm0
    # 求解一元二次方程
    # Ce是栅极的寄生=k.gm+cpar_in, RL是第二级的负载电阻=gain_pre/gm
    # Cmil是总的密勒=cmil+m.gm CL是总的负载=cl+n.gm
    # [ (1+A2)Cmil+Ce ] / { RL*(Cmil*Ce+Cmil*CL+Ce*CL) } = 6.18*fnd
    # 分子化简
    a2 = (k + m * (1 + gain_pre)) / gain_pre  # 二次系数
    a1 = (cpar_in + cmil * (1 + gain_pre)) / gain_pre
    # 分母化简，考虑乘以右侧的6.18*fnd
    b2 = (k * m + k * n + m * n) * 6.18 * fnd
    b1 = (k * cmil + k * cl + m * cl + m * cpar_in + n * cmil + n * cpar_in) * 6.18 * fnd
    b0 = (cpar_in * cmil + cmil * cl + cpar_in * cl) * 6.18 * fnd
    coeff2 = b2 - a2
    coeff1 = b1 - a1
    coeff0 = b0
    coeff = [coeff2, coeff1, coeff0]
    if coeff1 * coeff1 >= 4 * coeff2 * coeff0:  # 说明有解
        root = np.roots(coeff)
        if max(root) < 0:  # 等同于无解
            state_flag = 1
            return state_flag, 0, 0, 0, 0, 0, 0
        else:
            if min(root) > 0:
                gm_target = min(root)
            else:
                gm_target = max(root)
            finger = math.ceil(gm_target / gm0)
            pst.cir_modify('stage2_pz.sp', 24, finger)
            id_target = idp0 * finger
            cg_par = cgg2 * finger
            cc_par = ccx * finger  # 返回cc_par是因为这个要被当作总的cc提供给s1做负载
            return state_flag, 0, 0, 0, id_target, cg_par, cc_par
        # return state_flag, gm_cgg, gm_cgg_min, gain_pre, id_target, cg_par
    else:
        state_flag = 1
        return state_flag, 0, 0, 0, 0, 0, 0
