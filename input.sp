** Generated for: hspiceD
** Generated on: Jul 29 16:01:15 2019
** Design library name: smic18Work
** Design cell name: five_tube_gen
** Design view name: schematic

.PARAM LN= 1.39e-06
.PARAM LP= 4.65e-07
.PARAM WN= 0.0007683
.PARAM WP= 7.094e-05
.PARAM CL= 9.814e-11
.PARAM SUPPLY= 1.8
.PARAM VP= 0.3628
.PARAM VCMI= 0.9

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2
+    DCCAP=1 
+    POST
.LIB 'D:\synopsys\model\ms018_v1p7.lib' TT

MN1 VM      VIP 	VP 		0 			n18 L=LN W=WN
MN2 VOUT VIN 	VP 		0 			n18 L=LN W=WN
MP1 VM 	 VM  AVDD	AVDD p18 L=LP  W=WP
MP2 VOUT VM  AVDD	AVDD p18 L=LP  W=WP
C0 VOUT 0 CL

**vsource
V3 AVDD 0 DC=SUPPLY
V2 VCM VIP DC=0 AC=0.5 SIN(0 0.0002 1K) 
V1 VIN VCM DC=0 AC=0.5 SIN(0 0.0002 1K) 
V0 VP   0 DC=VP
VCM VCM 0 DC=VCMI

**Simulating
.OP brief 0
.AC DEC 500 1.0 100e9
.TRAN 1n 20m
.DC CL 1e-12 2e-12 1e-12

.PROBE V(VIN) V(VIP)
.PROBE V(VOUT) V(VM)
**Measure
.MEAS AC GBW WHEN VDB(VOUT)=0
.MEAS AC DcGain find V(VOUT) at 10
.MEAS DC IDS find par('lx4(MN1)') at 2e-12
.MEAS DC GMI find par('lx7(MN1)') at 2e-12
.MEAS DC cddn find par('lx33(MN2)') at 2e-12
.MEAS DC cddp find par('lx33(MP2)') at 2e-12
**Measure
**.MEAS DC vo1 find V(VOUT) at 2e-12

.END