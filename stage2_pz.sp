** Generated for: hspiceD Line0
** Generated on: Jul 29 16:01:15 2019
** Design library name: smic18Work
** the gain0 is in line 6!!!	LNP( Line7 ) is variable to sweep!  LNP0 (Line9) is a parameter.
** the SUPPLY is in line 11!!!


.PARAM LP2= 2.35e-07
.PARAM WP2= 5e-06
.PARAM LN2= 2.2e-07
.PARAM WN2= 6.832e-07
.PARAM LNP= 2.2e-07
.PARAM LNP0= 2.2e-07
.PARAM routid= 8.264
.PARAM gain0= 60.0
.PARAM WN= 6e-07
.PARAM WP= 6e-07
.PARAM VCMI= 0.9 
.PARAM VCMO= 0.9
.PARAM SUPPLY= 1.8
.PARAM CL= 5e-12
.PARAM CC= 3e-12
.PARAM gmid= 3.3
.PARAM VMID= 1.1
.PARAM FINGER= 115.0
.PARAM RZ= 0.1



** 下面的参数属于批量设置，不用于第二级扫描
.PARAM LN= 1.655e-06
.PARAM LP= 7.2e-07
.PARAM WN= 0.0003542
.PARAM WP= 0.0001569
.PARAM VP= 0.3028

**The copy of the parameter.


.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2
+    DCCAP=1 **想看寄生电容必须打开这个
+    POST ** POST选项使保存所有节点
.LIB 'D:\synopsys\model\ms018_v1p7.lib' TT

MN1 VM      VIN 	VP 		0 			n18 L=LN W=WN **这里的正负和单级的input.sp极性相反
MN2 VO1 VIP 	VP 		0 			n18 L=LN W=WN
MP1 VM 	 VM  AVDD	AVDD p18 L=LP  W=WP
MP2 VO1 VM  AVDD	AVDD p18 L=LP  W=WP
**CIMG1 VO1 VP 1e-12 ** 接一个1p的虚拟电容
**CIMG2 VM VP 1e-12 ** 接一个1p的虚拟电容

MP3 VOUT VO1 AVDD AVDD p18 m=FINGER L=LP2 W=WP2
MN3 VOUT VBN 0 0 n18 m=FINGER L=LN2 W=WN2
CLOAD VOUT 0 CL
CMIL VO1_RES VOUT CC
RMIL VO1 VO1_RES RZ

* 负输入端建立直流闭环
RIMG1 VIN 0 1e12 AC=0.1 **VIN端接一个DC无穷大，AC=0的电阻到地
RIMG2 VIN VOUT 0.1 AC=1e12 **跨接1个DC=0 AC无穷大的电阻

* 第二级尺寸确定电路，将两个管子漏端接到理想的VCMO上
MP4 VO3 VMID AVDD AVDD p18 L=LNP W=WP2
MN4 VO3 VBN 0 0 n18 L=LNP W=WN2

V0 AVDD 0 DC=SUPPLY
V1 VCM 0 DC=VCMI
V2 VIP VCM DC=0 AC=1 SIN(0 0.0002 1K)  ** VIP直接加一个AC=1的信号
** V3 VIN_RES 0 DC=0 AC=0 SIN(0 0.0002 1K) **VIP不接了，通过一个AC=0的电阻到地
V4 VP   0 DC=VP
V5 VBN 0 DC=0.8 **N管负载的偏置电压暂定700mV
V6 VO3 0 DC=VCMO **这是一个虚拟节点，设置为VCM0用来算P管的尺寸和N管的尺寸
V7 VMID 0 DC=VMID **这也是一个虚拟节点，在设计第一级之前，接在第二级的输入端，直接评估当前gain和cmil

**Simulating
*.OP brief 0
.OP
.AC DEC 500 1.0 100e9
.PROBE VP(VO1) VDB(VO1) VP(VOUT) VDB(VOUT) ** 注意，当查看相位曲线时，PRINT/PROBE函数必须跟随AC
.DC LNP 180n 10u 5n
**.probe cgstest=par('cgsbo(MP3)')
.PZ V(VOUT) V2


**Measure lx4=id	lx7=gm	lx8=gds lv9=vth
.MEAS DC gain_pre find par('lx7(MP4)/lx8(MP4)') at LNP0 **这个用来初始状态下观测P管的最小本征增益和后面验证增益
.MEAS DC LENGP WHEN  par('lx7(MP4)/lx8(MP4)') =gain0 ** 找到gmrout=gain0处的LNP值
.MEAS DC gm0 find par('lx7(MP4)') at LNP0 **命名为gm0是因为它是这个网表里第一个关注的gm
.MEAS DC idp0 find par('lx4(MP4)') at LNP0
.MEAS DC Proutid find par('lx4(MP4)/lx8(MP4)') at LNP0 **这个用来测增益确定后P管的routid
.MEAS DC LENGN WHEN  par('lx4(MN4)/lx8(MN4)') =routid
.MEAS DC idn0 find par('lx4(MN4)') at LNP0
.MEAS DC cgg0 find par('abs(lx20(MP4))+abs(lx21(MP4))') at LP2 **lx20是gs lx21是gb
.MEAS DC CL1   find par('abs(lx34(MP4))+abs(lx22(MP4)) ') at LP2 **Cds Cdb
.MEAS DC ccx find par('abs(lx19(MP4))') at LP2 **获取cgd作为cmil的补充
.MEAS DC CL2 find par('abs(lx33(MN4))') at LN2

.MEAS AC PHASEMARGIN FIND VP(VOUT) WHEN VDB(VOUT)=0
.MEAS AC GBW WHEN VDB(VOUT)=0
.MEAS AC ac_gain find V(VOUT) at 1

** 下面是debug用的MEAS，正式仿真时要删掉
**.MEAS DC ProutidX find par('lx4(MP4)/lx8(MP4)') at LP2
**.MEAS DC NroutidX find par('lx4(MN4)/lx8(MN4)') at LN2
**.MEAS DC idpx find par('lx4(MP4)') at LP2
**.MEAS DC idnx find par('lx4(MN4)') at LN2
.MEAS DC vo2 find V(VOUT) at LNP0
.MEAS DC vo1 find V(VO1) at LNP0
**.MEAS DC gm_mp3 find par('lx7(MP3)') at LP2
**.MEAS DC gm_mp4 find par('lx7(MP4)') at LP2
**.MEAS DC gm_mn2 find par('lx7(MN2)') at LP2
**.MEAS DC cgs_mp3 find par('lx18(MP3)') at LNP0 **lx18是gg lx20是gs
**.MEAS DC cdd_mp2 find par('lx33(MP2)') at LNP0 **lx33是dd
**.MEAS DC cdd_mn2 find par('lx33(MN2)') at LNP0 **lx33是dd
**.MEAS DC cdd_mp3 find par('lx33(MP3)') at LNP0
**.MEAS DC cdd_mn3 find par('lx33(MN3)') at LNP0
**.MEAS DC id_s1 find par('lx4(MN1)') at LNP0
**.MEAS DC id_s2 find par('lx4(MN3)') at LNP0
**.MEAS DC cgd_mp3 find par('lx19(MP3)') at LNP0
**.MEAS DC CE           find par('abs(lx33(MN2))+abs(lx33(MP2))+abs(lx20(MP3))+abs(lx21(MP3)) ') at LNP0 **Cdd Cgs Cgb
**.MEAS DC CL2         find par('abs(lx33(MN3))+abs(lx34(MP3))+abs(lx22(MP3)) ') at LNP0 **Cdd Cds Cdb

**.MEAS DC rout find par('1/lx8(MP3)') at LNP0
**.MEAS DC gain find par('lx7(MP3)/lx8(MP3)') at LNP0 ** 吐出LNP处的增益
**.MEAS DC LENGP WHEN  par('lx7(MP4)/lx8(MP4)') =gain0 ** 找到gmrout=gain0处的LNP值
**.MEAS DC Proutid find par('lx4(MP4)/lx8(MP4)') at LNP0
**.MEAS DC LENGN WHEN  par('lx4(MN4)/lx8(MN4)') =routid
**.MEAS DC IDP find par('lx4(MP4)') at LP2
**.MEAS DC IDN find par('lx4(MN4)') at LN2
**.MEAS DC GM_ID find par('lx7(MP3)/lx4(MP3)') at LNP0
**.MEAS DC vo2 find V(VOUT) at LNP0
**.MEAS DC vo1 find V(VO1) at LNP0
**.MEAS DC cgs2 find par('lx18(MP3)') at LNP0 **lx18是gg lx20是gs
**.MEAS DC is2 find par('lx4(MP3)') at LNP0
**.MEAS DC cdd1 find par('lx33(MP2)') at LNP0 **lx33是dd
**
**.MEAS DC Proutidx find par('lx4(MP4)/lx8(MP4)') at LP2
**.MEAS DC Nroutidx find par('lx4(MN4)/lx8(MN4)') at LN2
**.MEAS DC gm_s1 find par('lx7(MN1)') at LNP0
.END