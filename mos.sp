** Generated for: hspiceD Line0
** Generated on: Jul 29 16:01:15 2019
** Design library name: smic18Work
** the gain0 is in line 6!!!	LNP( Line7 ) is variable to sweep!  LNP0 (Line9) is a parameter.
** the SUPPLY is in line 11!!!

.PARAM gain0= 353.5
.PARAM LNP= 4.65e-07
.PARAM routid= 17.3
.PARAM LNP0= 4.65e-07
.PARAM WN= 0.009401
.PARAM WP= 0.000868
**The above will be modified by code while the below is preset by user.
.PARAM VCMI= 0.9 
.PARAM VCMO= 1.1
.PARAM SUPPLY= 1.8
.PARAM VP= 0.3628
.PARAM LSWEEP= 1.601e-06

**The copy of the parameter.


.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2
.LIB 'D:\synopsys\model\ms018_v1p7.lib' TT


MN1 VCMO VCMI VP 0 n18 L=LNP W=WN 
MP1 VCMO VCMO AVDD AVDD p18 L=LNP W=WP

**vsource
V3 AVDD 0 DC=SUPPLY
V2 VCMI 0 DC=VCMI
V1 VCMO 0 DC=VCMO
V0 VP 0 DC=VP

**Simulating
.OP brief 0
*.AC DEC 500 1.0 100e9
.DC LNP 180n LSWEEP 5n

**Measure lx4=id	lx7=gm	lx8=gds lv9=vth
**.MEAS AC GBW WHEN VDB(VOUT)=0
**.MEAS AC DcGain find V(VOUT) at 10

.MEAS DC gain find par('lx7(MN1)/lx8(MN1)') at LNP0 ** 吐出LNP0处的增益
.MEAS DC LENGN WHEN  par('lx7(MN1)/lx8(MN1)') =gain0 ** 找到gmrout=gain0处的LNP值
.MEAS DC Nroutid find par('lx4(MN1)/lx8(MN1)') at LNP0
.MEAS DC LENGP WHEN par('lx4(MP1)/lx8(MP1)') =routid
.MEAS DC IDN find par('lx4(MN1)') at LNP0
.MEAS DC IDP find par('lx4(MP1)') at LNP0
.MEAS DC VTHN find par('lv9(MN1)') at LNP0 **找到默认状态下的vth0
.MEAS DC GM_ID find par('lx7(MN1)/lx4(MN1)') at LNP0

** 测试用，这两个变量随便定义，不会被读取
.MEAS DC Proutid find par('lx4(MP1)/lx8(MP1)') at 180e-9 **判断最小的P尺寸
.MEAS DC gmn find par('lx7(MN1)') at LNP0
**.MEAS DC ID find par('lx4(MN1)') at LNP0

**.MEAS DC Proutid find par('lx4(MP1)/lx8(MP1)') at 6.25e-7
**.MEAS DC vgt find par('lx2(MN1)-lv9(MN1)') at LNP

**Measure

.END