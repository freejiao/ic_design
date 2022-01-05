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



** ����Ĳ��������������ã������ڵڶ���ɨ��
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
+    DCCAP=1 **�뿴�������ݱ�������
+    POST ** POSTѡ��ʹ�������нڵ�
.LIB 'D:\synopsys\model\ms018_v1p7.lib' TT

MN1 VM      VIN 	VP 		0 			n18 L=LN W=WN **����������͵�����input.sp�����෴
MN2 VO1 VIP 	VP 		0 			n18 L=LN W=WN
MP1 VM 	 VM  AVDD	AVDD p18 L=LP  W=WP
MP2 VO1 VM  AVDD	AVDD p18 L=LP  W=WP
**CIMG1 VO1 VP 1e-12 ** ��һ��1p���������
**CIMG2 VM VP 1e-12 ** ��һ��1p���������

MP3 VOUT VO1 AVDD AVDD p18 m=FINGER L=LP2 W=WP2
MN3 VOUT VBN 0 0 n18 m=FINGER L=LN2 W=WN2
CLOAD VOUT 0 CL
CMIL VO1_RES VOUT CC
RMIL VO1 VO1_RES RZ

* ������˽���ֱ���ջ�
RIMG1 VIN 0 1e12 AC=0.1 **VIN�˽�һ��DC�����AC=0�ĵ��赽��
RIMG2 VIN VOUT 0.1 AC=1e12 **���1��DC=0 AC�����ĵ���

* �ڶ����ߴ�ȷ����·������������©�˽ӵ������VCMO��
MP4 VO3 VMID AVDD AVDD p18 L=LNP W=WP2
MN4 VO3 VBN 0 0 n18 L=LNP W=WN2

V0 AVDD 0 DC=SUPPLY
V1 VCM 0 DC=VCMI
V2 VIP VCM DC=0 AC=1 SIN(0 0.0002 1K)  ** VIPֱ�Ӽ�һ��AC=1���ź�
** V3 VIN_RES 0 DC=0 AC=0 SIN(0 0.0002 1K) **VIP�����ˣ�ͨ��һ��AC=0�ĵ��赽��
V4 VP   0 DC=VP
V5 VBN 0 DC=0.8 **N�ܸ��ص�ƫ�õ�ѹ�ݶ�700mV
V6 VO3 0 DC=VCMO **����һ������ڵ㣬����ΪVCM0������P�ܵĳߴ��N�ܵĳߴ�
V7 VMID 0 DC=VMID **��Ҳ��һ������ڵ㣬����Ƶ�һ��֮ǰ�����ڵڶ���������ˣ�ֱ��������ǰgain��cmil

**Simulating
*.OP brief 0
.OP
.AC DEC 500 1.0 100e9
.PROBE VP(VO1) VDB(VO1) VP(VOUT) VDB(VOUT) ** ע�⣬���鿴��λ����ʱ��PRINT/PROBE�����������AC
.DC LNP 180n 10u 5n
**.probe cgstest=par('cgsbo(MP3)')
.PZ V(VOUT) V2


**Measure lx4=id	lx7=gm	lx8=gds lv9=vth
.MEAS DC gain_pre find par('lx7(MP4)/lx8(MP4)') at LNP0 **���������ʼ״̬�¹۲�P�ܵ���С��������ͺ�����֤����
.MEAS DC LENGP WHEN  par('lx7(MP4)/lx8(MP4)') =gain0 ** �ҵ�gmrout=gain0����LNPֵ
.MEAS DC gm0 find par('lx7(MP4)') at LNP0 **����Ϊgm0����Ϊ��������������һ����ע��gm
.MEAS DC idp0 find par('lx4(MP4)') at LNP0
.MEAS DC Proutid find par('lx4(MP4)/lx8(MP4)') at LNP0 **�������������ȷ����P�ܵ�routid
.MEAS DC LENGN WHEN  par('lx4(MN4)/lx8(MN4)') =routid
.MEAS DC idn0 find par('lx4(MN4)') at LNP0
.MEAS DC cgg0 find par('abs(lx20(MP4))+abs(lx21(MP4))') at LP2 **lx20��gs lx21��gb
.MEAS DC CL1   find par('abs(lx34(MP4))+abs(lx22(MP4)) ') at LP2 **Cds Cdb
.MEAS DC ccx find par('abs(lx19(MP4))') at LP2 **��ȡcgd��Ϊcmil�Ĳ���
.MEAS DC CL2 find par('abs(lx33(MN4))') at LN2

.MEAS AC PHASEMARGIN FIND VP(VOUT) WHEN VDB(VOUT)=0
.MEAS AC GBW WHEN VDB(VOUT)=0
.MEAS AC ac_gain find V(VOUT) at 1

** ������debug�õ�MEAS����ʽ����ʱҪɾ��
**.MEAS DC ProutidX find par('lx4(MP4)/lx8(MP4)') at LP2
**.MEAS DC NroutidX find par('lx4(MN4)/lx8(MN4)') at LN2
**.MEAS DC idpx find par('lx4(MP4)') at LP2
**.MEAS DC idnx find par('lx4(MN4)') at LN2
.MEAS DC vo2 find V(VOUT) at LNP0
.MEAS DC vo1 find V(VO1) at LNP0
**.MEAS DC gm_mp3 find par('lx7(MP3)') at LP2
**.MEAS DC gm_mp4 find par('lx7(MP4)') at LP2
**.MEAS DC gm_mn2 find par('lx7(MN2)') at LP2
**.MEAS DC cgs_mp3 find par('lx18(MP3)') at LNP0 **lx18��gg lx20��gs
**.MEAS DC cdd_mp2 find par('lx33(MP2)') at LNP0 **lx33��dd
**.MEAS DC cdd_mn2 find par('lx33(MN2)') at LNP0 **lx33��dd
**.MEAS DC cdd_mp3 find par('lx33(MP3)') at LNP0
**.MEAS DC cdd_mn3 find par('lx33(MN3)') at LNP0
**.MEAS DC id_s1 find par('lx4(MN1)') at LNP0
**.MEAS DC id_s2 find par('lx4(MN3)') at LNP0
**.MEAS DC cgd_mp3 find par('lx19(MP3)') at LNP0
**.MEAS DC CE           find par('abs(lx33(MN2))+abs(lx33(MP2))+abs(lx20(MP3))+abs(lx21(MP3)) ') at LNP0 **Cdd Cgs Cgb
**.MEAS DC CL2         find par('abs(lx33(MN3))+abs(lx34(MP3))+abs(lx22(MP3)) ') at LNP0 **Cdd Cds Cdb

**.MEAS DC rout find par('1/lx8(MP3)') at LNP0
**.MEAS DC gain find par('lx7(MP3)/lx8(MP3)') at LNP0 ** �³�LNP��������
**.MEAS DC LENGP WHEN  par('lx7(MP4)/lx8(MP4)') =gain0 ** �ҵ�gmrout=gain0����LNPֵ
**.MEAS DC Proutid find par('lx4(MP4)/lx8(MP4)') at LNP0
**.MEAS DC LENGN WHEN  par('lx4(MN4)/lx8(MN4)') =routid
**.MEAS DC IDP find par('lx4(MP4)') at LP2
**.MEAS DC IDN find par('lx4(MN4)') at LN2
**.MEAS DC GM_ID find par('lx7(MP3)/lx4(MP3)') at LNP0
**.MEAS DC vo2 find V(VOUT) at LNP0
**.MEAS DC vo1 find V(VO1) at LNP0
**.MEAS DC cgs2 find par('lx18(MP3)') at LNP0 **lx18��gg lx20��gs
**.MEAS DC is2 find par('lx4(MP3)') at LNP0
**.MEAS DC cdd1 find par('lx33(MP2)') at LNP0 **lx33��dd
**
**.MEAS DC Proutidx find par('lx4(MP4)/lx8(MP4)') at LP2
**.MEAS DC Nroutidx find par('lx4(MN4)/lx8(MN4)') at LN2
**.MEAS DC gm_s1 find par('lx7(MN1)') at LNP0
.END