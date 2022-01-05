import re  # 字符串相关
import os  # to exec hspice
import math
import gc
import sys


def getResuSeed(meas_file, line_num, para_num):
    # line_num represent the line to be picked.
    # For the measure file,the final line(-1) should be picked.
    # For the simulate file,the line where parameter lies should be picked and modified.
    # meas_file=sys.argv[1]
    # para_num=sys.argv[2]
    handle0 = open(meas_file)
    # In python3,the file method is replaced by open
    lines = handle0.readlines(-1)
    para = lines[line_num]
    para_list = para.split()
    #	para_list=list(map(float,para_list))
    #	para_return=para_list[para_num]#must be called by square bracket
    para_list = para_list[para_num]
    if para_list != 'failed':  # 如果结果不是failed就float处理并返回
        para_return = float(para_list)
    else:
        para_return = 'failed'
    return para_return


def getPole(infilePath, outfilePath):
    with open(infilePath, 'r') as fin:
        lines = fin.readlines()
        for num, value in enumerate(lines):
            lineList = value.strip().split(' ')
            if lineList[0] == 'poles':
                print("获取到poles行，行号是%s" % num)
                outContents = []
                for i in range(2, 100):
                    if lines[num + i].strip() == '':
                        break
                    outContents.append(lines[num + i])
                outContents.append('\n')
                fout = open(outfilePath, 'w+')
                for content in outContents:
                    fout.write(content)
                fout.close()
    print("处理完毕，输出文件为：%s" % outfilePath)


def getZero(infilePath, outfilePath):
    with open(infilePath, 'r') as fin:
        lines = fin.readlines()
        for num, value in enumerate(lines):
            lineList = value.strip().split(' ')
            if lineList[0] == 'zeros':
                print("获取到zeros行，行号是%s" % num)
                outContents = []
                for i in range(2, 100):
                    if lines[num + i].strip() == '':
                        break
                    outContents.append(lines[num + i])
                outContents.append('\n')
                fout = open(outfilePath, 'w+')
                for content in outContents:
                    fout.write(content)
                fout.close()
    print("处理完毕，输出文件为：%s" % outfilePath)

def getResuPz(meas_file, line_num, para_num):
    # 三种情况：k x g
    # line_num represent the line to be picked.
    # For the measure file,the final line(-1) should be picked.
    # For the simulate file,the line where parameter lies should be picked and modified.
    # meas_file=sys.argv[1]
    # para_num=sys.argv[2]
    handle0 = open(meas_file)
    # In python3,the file method is replaced by open
    lines = handle0.readlines(-1)
    para = lines[line_num]
    para_list = para.split()
    para_list = para_list[para_num]
    unit = para_list[len(para_list) - 1]
    value = para_list[:-1]
    para_return = float(value)
    if unit == 'k':
        para_return = para_return * 1e3
    else:
        if unit == 'x':
            para_return = para_return * 1e6
        else:
            if unit == 'g':
                para_return = para_return * 1e9
            else:
                para_return = 'failed'
    return para_return

def cir_modify(meas_file, line_num, para_value):
    # 输入spice文件名、行号以及新的参数值即可
    para_value = float('%.4g' % para_value)  # 先取4位有效数字
    pseudo = meas_file + "pseudo"
    handle0 = open(meas_file)
    lines = handle0.readlines(-1)
    para = lines[line_num]
    handle0.close()
    # by the line gotten,get the new line to replace.
    para_list = para.split()
    para_list[2] = str(para_value)
    para_new = para_list[0] + ' ' + para_list[1] + ' ' + para_list[2] + '\n'
    open(pseudo, 'w').write(re.sub(para, para_new, open(meas_file).read()))
    os.remove(meas_file)
    os.rename(pseudo, meas_file)


def real_modify(ln, lp, wn, wp, meas_file):
    # put the parameter gotten into the real circuit.
    cir_modify(meas_file, 6, ln)
    cir_modify(meas_file, 7, lp)
    cir_modify(meas_file, 8, wn)
    cir_modify(meas_file, 9, wp)


def getResu(meas_file, resu_name):
    # 输入文件名，参数名，此函数根据不同的输出结果和measure的参数顺序，返回值
    if meas_file == 'mos.ms0':  # 读取mos.ms0，则参考mos.ms0的数据定义
        if resu_name == 'gain':
            data = getResuSeed(meas_file, -3, 0)
        if resu_name == 'lengn':
            data = getResuSeed(meas_file, -3, 1)
        if resu_name == 'nroutid':
            data = getResuSeed(meas_file, -3, 2)
        if resu_name == 'lengp':
            data = getResuSeed(meas_file, -3, 3)

        if resu_name == 'idn':
            data = getResuSeed(meas_file, -2, 0)
        if resu_name == 'idp':
            data = getResuSeed(meas_file, -2, 1)
        if resu_name == 'vthn':
            data = getResuSeed(meas_file, -2, 2)
        if resu_name == 'gm_id':
            data = getResuSeed(meas_file, -2, 3)

        if resu_name == 'proutid':
            data = getResuSeed(meas_file, -1, 0)
        if resu_name == 'gmn':
            data = getResuSeed(meas_file, -1, 1)

    if meas_file == 'input.ma0':  # 读取input.ma0，这是用来存放AC meas结果的
        if resu_name == 'gbw':
            data = getResuSeed(meas_file, -1, 0)
        if resu_name == 'gain':
            data = getResuSeed(meas_file, -1, 1)

    if meas_file == 'input.ms0':  # 读取input.ms0，这是用来存放dc meas结果的
        if resu_name == 'id':
            data = 2 * getResuSeed(meas_file, -2, 0)
        if resu_name == 'gm':
            data = getResuSeed(meas_file, -2, 1)
        if resu_name == 'cddn':
            data = getResuSeed(meas_file, -2, 2)
        if resu_name == 'cddp':
            data = getResuSeed(meas_file, -2, 3)

    if meas_file == 'stage2_pz.ms0':  # 读取最终电路的直流扫描结果
        if resu_name == 'gain_pre':
            data = getResuSeed(meas_file, -4, 0)
        if resu_name == 'lengp':
            data = getResuSeed(meas_file, -4, 1)
        if resu_name == 'gm0':
            data = getResuSeed(meas_file, -4, 2)
        if resu_name == 'idp0':
            data = getResuSeed(meas_file, -4, 3)
        if resu_name == 'proutid':
            data = getResuSeed(meas_file, -3, 0)
        if resu_name == 'lengn':
            data = getResuSeed(meas_file, -3, 1)
        if resu_name == 'idn0':
            data = getResuSeed(meas_file, -3, 2)
        if resu_name == 'cggp':
            data = getResuSeed(meas_file, -3, 3)
        if resu_name == 'clx':  # 这里获取输出级带来的额外负载，直接把两部分合起来
            data = getResuSeed(meas_file, -2, 0) + getResuSeed(meas_file, -2, 2)
        if resu_name == 'ccx':
            data = getResuSeed(meas_file, -2, 1)
        if resu_name == 'cddn':  # 后面如果要优化N管负载的偏置电压，直接取出即可
            data = getResuSeed(meas_file, -2, 2)

    if meas_file == 'stage2_pz.ma0':  # 读取最终电路的交流扫描结果
        if resu_name == 'pm':
            data = getResuSeed(meas_file, -2, 0)
        if resu_name == 'gbw':
            data = getResuSeed(meas_file, -2, 1)
        if resu_name == 'ac_gain':
            data = getResuSeed(meas_file, -2, 2)
    return data
