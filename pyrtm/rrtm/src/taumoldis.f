C     path:      $Source: /storm/rc1/cvsroot/rc/rrtm_sw/src/taumoldis.f,v $
C     author:    $Author: jdelamer $
C     revision:  $Revision: 2.5 $
C     created:   $Date: 2004/04/15 18:50:57 $

C
C  --------------------------------------------------------------------------
C |                                                                          |
C |  Copyright 2002, 2003, Atmospheric & Environmental Research, Inc. (AER). |
C |  This software may be used, copied, or redistributed as long as it is    |
C |  not sold and this copyright notice is reproduced on each copy made.     |
C |  This model is provided as is without any express or implied warranties. |
C |                       (http://www.rtweb.aer.com/)                        |
C |                                                                          |
C  --------------------------------------------------------------------------

*******************************************************************************
*                                                                             *
*                  Optical depths developed for the                           *
*                                                                             *
*                RAPID RADIATIVE TRANSFER MODEL (RRTM)                        *
*                                                                             *
*                                                                             *
*            ATMOSPHERIC AND ENVIRONMENTAL RESEARCH, INC.                     *
*                        840 MEMORIAL DRIVE                                   *
*                        CAMBRIDGE, MA 02139                                  *
*                                                                             *
*                                                                             *
*                           ELI J. MLAWER                                     *
*                         STEVEN J. TAUBMAN                                   *
*                         SHEPARD A. CLOUGH                                   *
*                                                                             *
*                                                                             *
*                                                                             *
*                                                                             *
*                       email:  mlawer@aer.com                                *
*                                                                             *
*        The authors wish to acknowledge the contributions of the             *
*        following people:  Patrick D. Brown, Michael J. Iacono,              *
*        Ronald E. Farren, Luke Chen, Robert Bergstrom.                       *
*                                                                             *
*******************************************************************************
*     TAUMOL                                                                  *
*                                                                             *
*     This file contains the subroutines TAUGBn (where n goes from            *
*     1 to 28).  TAUGBn calculates the optical depths and Planck fractions    *
*     per g-value and layer for band n.                                       *
*                                                                             *
*  Output:  optical depths (unitless)                                         *
*           fractions needed to compute Planck functions at every layer       *
*               and g-value                                                   *
*                                                                             *
*     COMMON /TAUGCOM/  TAUG(MXLAY,MG)                                        *
*     COMMON /PLANKG/   FRACS(MXLAY,MG)                                       *
*                                                                             *
*  Input                                                                      *
*                                                                             *
*     COMMON /FEATURES/ NG(NBANDS),NSPA(NBANDS),NSPB(NBANDS)                  *
*     COMMON /PRECISE/  ONEMINUS                                              *
*     COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),                    *
*    &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND                        *
*     COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,                              *
*    &                  COLH2O(MXLAY),COLCO2(MXLAY),                          *
*    &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),             *
*    &                  COLO2(MXLAY),CO2MULT(MXLAY)                           *
*     COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            *
*    &                  FAC10(MXLAY),FAC11(MXLAY)                             *
*     COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)                        *
*     COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)       *
*                                                                             *
*     Description:                                                            *
*     NG(IBAND) - number of g-values in band IBAND                            *
*     NSPA(IBAND) - for the lower atmosphere, the number of reference         *
*                   atmospheres that are stored for band IBAND per            *
*                   pressure level and temperature.  Each of these            *
*                   atmospheres has different relative amounts of the         *
*                   key species for the band (i.e. different binary           *
*                   species parameters).                                      *
*     NSPB(IBAND) - same for upper atmosphere                                 *
*     ONEMINUS - since problems are caused in some cases by interpolation     *
*                parameters equal to or greater than 1, for these cases       *
*                these parameters are set to this value, slightly < 1.        *
*     PAVEL - layer pressures (mb)                                            *
*     TAVEL - layer temperatures (degrees K)                                  *
*     PZ - level pressures (mb)                                               *
*     TZ - level temperatures (degrees K)                                     *
*     LAYTROP - layer at which switch is made from one combination of         *
*               key species to another                                        *
*     COLH2O, COLCO2, COLO3, COLN2O, COLCH4 - column amounts of water         *
*               vapor,carbon dioxide, ozone, nitrous ozide, methane,          *
*               respectively (molecules/cm**2)                                *
*     CO2MULT - for bands in which carbon dioxide is implemented as a         *
*               trace species, this is the factor used to multiply the        *
*               band's average CO2 absorption coefficient to get the added    *
*               contribution to the optical depth relative to 355 ppm.        *
*     FACij(LAY) - for layer LAY, these are factors that are needed to        *
*                  compute the interpolation factors that multiply the        *
*                  appropriate reference k-values.  A value of 0 (1) for      *
*                  i,j indicates that the corresponding factor multiplies     *
*                  reference k-value for the lower (higher) of the two        *
*                  appropriate temperatures, and altitudes, respectively.     *
*     JP - the index of the lower (in altitude) of the two appropriate        *
*          reference pressure levels needed for interpolation                 *
*     JT, JT1 - the indices of the lower of the two appropriate reference     *
*               temperatures needed for interpolation (for pressure           *
*               levels JP and JP+1, respectively)                             *
*     SELFFAC - scale factor needed to water vapor self-continuum, equals     *
*               (water vapor density)/(atmospheric density at 296K and        *
*               1013 mb)                                                      *
*     SELFFRAC - factor needed for temperature interpolation of reference     *
*                water vapor self-continuum data                              *
*     INDSELF - index of the lower of the two appropriate reference           *
*               temperatures needed for the self-continuum interpolation      *
*                                                                             *
*  Data input                                                                 *
*     COMMON /Kn/ KA(NSPA(n),5,13,MG), KB(NSPB(n),5,13:59,MG), SELFREF(10,MG) *
*        (note:  n is the band number)                                        *
*                                                                             *
*     Description:                                                            *
*     KA - k-values for low reference atmospheres (no water vapor             *
*          self-continuum) (units: cm**2/molecule)                            *
*     KB - k-values for high reference atmospheres (all sources)              *
*          (units: cm**2/molecule)                                            *
*     SELFREF - k-values for water vapor self-continuum for reference         *
*               atmospheres (used below LAYTROP)                              *
*               (units: cm**2/molecule)                                       *
*                                                                             *
*     DIMENSION ABSA(65*NSPA(n),MG), ABSB(235*NSPB(n),MG)                     *
*     EQUIVALENCE (KA,ABSA),(KB,ABSB)                                         *
*                                                                             *
*******************************************************************************

      SUBROUTINE TAUGB16

C     BAND 16:  2600-3250 cm-1 (low - H2O,CH4; high - CH4)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K16/      KA(9,5,13,MG),KB(5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(3,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG), ABSB(235,MG), SFLUXREF(MG)

C     Rayleigh extinction coefficient at v = 2925 cm-1.
      DATA RAYL /2.91E-10/

      DATA SFLUXREF/
C     Kurucz
     &     1.92269, 1.72844, 1.64326, 1.58451,
     &     1.44031, 1.25108, 1.02724,0.776759,
     &     0.534444, 5.87755E-02, 4.86706E-02, 3.87989E-02,
     &     2.84532E-02, 1.82431E-02, 6.92320E-03, 9.70770E-04/

      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT1 = 252.131
      LAYREFFR = 18

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      DO 2500 LAY = 1, LAYTROP
         SPECCOMB = COLH2O(LAY) + STRRAT1*COLCH4(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(16) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(16) + JS
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(16)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG)) +
     &           COLH2O(LAY) * 
     &           (SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 2000    CONTINUE
 2500 CONTINUE

      LAYSOLFR = NLAYERS
      DO 3500 LAY = LAYTROP+1, NLAYERS
         IF (JP(LAY-1) .LT. LAYREFFR .AND. JP(LAY) .GE. LAYREFFR) 
     &        LAYSOLFR = LAY
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(16) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(16) + 1
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(16)
            TAUG(LAY,IG) = COLCH4(LAY) *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG) 
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB17


C     BAND 17:  3250-4000 cm-1 (low - H2O,CO2; high - H2O,CO2)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K17/      KA(9,5,13,MG),KB(5,5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(4,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG),ABSB(1175,MG),SFLUXREF(MG,5)

C     Rayleigh extinction coefficient at v = 3625 cm-1.
      DATA RAYL /6.86E-10/

      DATA SFLUXREF/
C     Kurucz
     &     3.15613, 3.03449, 2.92069, 2.63874,
     &     2.34581, 2.06999, 1.70906, 1.29085,
     &     0.874851, 0.0955392, 0.0787813, 0.0621951,
     &     0.0459076, 0.0294129, 0.0110387, 0.00159668,
     &     2.83147, 2.95919, 2.96674, 2.77677,
     &     2.46826, 2.11481, 1.73243, 1.30279,
     &     0.882714, 0.0962350, 0.0802122, 0.0636194,
     &     0.0472620, 0.0299051, 0.0110785, 0.00159668,
     &     2.82300, 2.94845, 2.95887, 2.77593,
     &     2.47096, 2.12596, 1.73847, 1.30796,
     &     0.884395, 0.0966936, 0.0801996, 0.0640199,
     &     0.0472803, 0.0300515, 0.0112366, 0.00160814,
     &     2.81715, 2.93789, 2.95091, 2.77046,
     &     2.47716, 2.13591, 1.74365, 1.31277,
     &     0.887443, 0.0967016, 0.0803391, 0.0642442,
     &     0.0472909, 0.0300720, 0.0114817, 0.00161875,
     &     2.82335, 2.93168, 2.91455, 2.75213,
     &     2.49168, 2.14408, 1.75726, 1.32401,
     &     0.893644, 0.0969523, 0.0805197, 0.0639936,
     &     0.0475099, 0.0305667, 0.0115372, 0.00161875/

      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA,KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT = 0.364641
      LAYREFFR = 30

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      DO 2500 LAY = 1, LAYTROP
         SPECCOMB = COLH2O(LAY) + STRRAT*COLCO2(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(17) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(17) + JS
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(17)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG)) +
     &           COLH2O(LAY) * 
     &           (SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 2000    CONTINUE
 2500 CONTINUE

      LAYSOLFR = NLAYERS
      DO 3500 LAY = LAYTROP+1, NLAYERS
         IF (JP(LAY-1) .LT. LAYREFFR .AND. JP(LAY) .GE. LAYREFFR) 
     &        LAYSOLFR = LAY
         SPECCOMB = COLH2O(LAY) + STRRAT*COLCO2(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 4.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(17) + JS
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(17) + JS
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(17)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSB(IND0,IG) +
     &           FAC100 * ABSB(IND0+1,IG) +
     &           FAC010 * ABSB(IND0+5,IG) +
     &           FAC110 * ABSB(IND0+6,IG) +
     &           FAC001 * ABSB(IND1,IG) + 
     &           FAC101 * ABSB(IND1+1,IG) +
     &           FAC011 * ABSB(IND1+5,IG) +
     &           FAC111 * ABSB(IND1+6,IG)) +
     &           COLH2O(LAY) * 
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG)))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG,JS) 
     &           + FS * (SFLUXREF(IG,JS+1) - SFLUXREF(IG,JS))
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END
C----------------------------------------------------------------------------

      SUBROUTINE TAUGB18

C     BAND 18:  4000-4650 cm-1 (low - H2O,CH4; high - CH4)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K18/      KA(9,5,13,MG),KB(5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(3,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG), ABSB(235,MG), SFLUXREF(MG,9)

C     Rayleigh extinction coefficient at v = 4325 cm-1.
      DATA RAYL /1.39E-09/

      DATA SFLUXREF/
C     Kurucz
     &     3.65840, 3.54375, 3.34481, 3.10534,
     &     2.79879, 2.42841, 1.98748, 1.49377,
     &     1.00196,0.108342, 8.95099E-02, 7.05199E-02,
     &     5.16432E-02, 3.27635E-02, 1.25133E-02, 1.73001E-03,
     &     3.86372, 3.48521, 3.30790, 3.08103,
     &     2.77552, 2.40722, 1.97307, 1.48023,
     &     0.993055,0.107691, 8.84430E-02, 6.99354E-02,
     &     5.07881E-02, 3.24121E-02, 1.19442E-02, 1.57612E-03,
     &     3.90370, 3.50657, 3.30629, 3.06046,
     &     2.76982, 2.39907, 1.96358, 1.47458,
     &     0.988475,0.106698, 8.75242E-02, 6.85898E-02,
     &     5.04798E-02, 3.13718E-02, 1.09533E-02, 1.57612E-03,
     &     3.93165, 3.52058, 3.31346, 3.04944,
     &     2.76074, 2.39433, 1.95556, 1.46712,
     &     0.984056,0.105885, 8.73062E-02, 6.84054E-02,
     &     4.87443E-02, 2.99295E-02, 1.09533E-02, 1.57612E-03,
     &     3.94082, 3.55221, 3.31863, 3.04730,
     &     2.74918, 2.38328, 1.95212, 1.45889,
     &     0.978888,0.105102, 8.65732E-02, 6.74563E-02,
     &     4.76592E-02, 2.91017E-02, 1.09533E-02, 1.57612E-03,
     &     3.94198, 3.58743, 3.32106, 3.05866,
     &     2.74115, 2.36939, 1.94305, 1.45180,
     &     0.971784, 1.04045E-01, 8.53731E-02, 6.60654E-02,
     &     4.63228E-02, 2.91016E-02, 1.09552E-02, 1.57612E-03,
     &     3.93596, 3.63366, 3.33144, 3.06252,
     &     2.74054, 2.35492, 1.92769, 1.44300,
     &     0.961809, 1.02867E-01, 8.34164E-02, 6.41005E-02,
     &     4.61826E-02, 2.91006E-02, 1.09553E-02, 1.57612E-03,
     &     3.92520, 3.69078, 3.35656, 3.07055,
     &     2.73862, 2.34430, 1.90187, 1.42242,
     &     0.946676, 9.96302E-02, 8.14421E-02, 6.38622E-02,
     &     4.61794E-02, 2.91017E-02, 1.09553E-02, 1.57612E-03,
     &     3.80721, 3.74437, 3.50205, 3.18009,
     &     2.75757, 2.29188, 1.84382, 1.35694,
     &     0.914040, 9.86811E-02, 8.14321E-02, 6.38541E-02,
     &     4.61795E-02, 2.90960E-02, 1.09613E-02, 1.57612E-03/

      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT = 38.9589
      LAYREFFR = 6

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         SPECCOMB = COLH2O(LAY) + STRRAT*COLCH4(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(18) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(18) + JS
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(18)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG)) +
     &           COLH2O(LAY) * 
     &           (SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG,JS) 
     &           + FS * (SFLUXREF(IG,JS+1) - SFLUXREF(IG,JS))
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(18) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(18) + 1
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(18)
            TAUG(LAY,IG) = COLCH4(LAY) *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END
C----------------------------------------------------------------------------

      SUBROUTINE TAUGB19

C     BAND 19:  4650-5150 cm-1 (low - H2O,CO2; high - CO2)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K19/      KA(9,5,13,MG),KB(5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(3,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG), ABSB(235,MG), SFLUXREF(MG,9)

C     Rayleigh extinction coefficient at v = 4900 cm-1.
      DATA RAYL /2.29E-09/

      DATA SFLUXREF/
C     Planck
C     Kurucz
     &     3.25791, 3.29697, 3.16031, 2.96115,
     &     2.69238, 2.33819, 1.92760, 1.44918,
     &     0.979764,0.107336, 8.94523E-02, 6.98325E-02,
     &     5.12051E-02, 3.23645E-02, 1.23401E-02, 1.71339E-03,
     &     3.22769, 3.28817, 3.16687, 2.97662,
     &     2.69495, 2.34392, 1.92900, 1.45391,
     &     0.982522,0.107638, 8.92458E-02, 6.99885E-02,
     &     5.09679E-02, 3.23789E-02, 1.22673E-02, 1.56040E-03,
     &     3.22294, 3.27780, 3.17424, 2.97143,
     &     2.69785, 2.34993, 1.93155, 1.45196,
     &     0.985329,0.108027, 8.93552E-02, 6.99937E-02,
     &     5.11678E-02, 3.24846E-02, 1.20636E-02, 1.56040E-03,
     &     3.22445, 3.26113, 3.18438, 2.96921,
     &     2.69579, 2.35586, 1.93454, 1.44949,
     &     0.987347,0.108611, 8.91643E-02, 7.02236E-02,
     &     5.12980E-02, 3.25282E-02, 1.21189E-02, 1.56040E-03,
     &     3.22497, 3.25109, 3.18741, 2.96970,
     &     2.69460, 2.36020, 1.93301, 1.45224,
     &     0.988564,0.108255, 8.93830E-02, 7.03655E-02,
     &     5.13017E-02, 3.29414E-02, 1.21189E-02, 1.56040E-03,
     &     3.22632, 3.24174, 3.18524, 2.97402,
     &     2.69807, 2.35742, 1.93377, 1.45621,
     &     0.988132,0.108344, 8.93188E-02, 7.04907E-02,
     &     5.17938E-02, 3.31465E-02, 1.21155E-02, 1.56040E-03,
     &     3.22793, 3.23589, 3.17720, 2.97869,
     &     2.70293, 2.35436, 1.93557, 1.45868,
     &     0.988654,0.108198, 8.93375E-02, 7.09790E-02,
     &     5.24733E-02, 3.31298E-02, 1.21126E-02, 1.56040E-03,
     &     3.22966, 3.24087, 3.15676, 2.98171,
     &     2.70894, 2.34975, 1.93855, 1.46354,
     &     0.988544,0.108574, 9.02522E-02, 7.12908E-02,
     &     5.24844E-02, 3.31084E-02, 1.21060E-02, 1.56040E-03,
     &     3.27240, 3.24666, 3.13886, 2.95238,
     &     2.70190, 2.34460, 1.93948, 1.47111,
     &     0.990821,0.108730, 9.01625E-02, 7.13261E-02,
     &     5.24813E-02, 3.31083E-02, 1.21126E-02, 1.56040E-03/

      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT = 5.49281
      LAYREFFR = 3

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         SPECCOMB = COLH2O(LAY) + STRRAT*COLCO2(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(19) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(19) + JS
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(19)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG)) +
     &           COLH2O(LAY) * 
     &           (SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG,JS) 
     &           + FS * (SFLUXREF(IG,JS+1) - SFLUXREF(IG,JS))
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(19) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(19) + 1
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(19)
            TAUG(LAY,IG) = COLCO2(LAY) *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG) 
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB20

C     BAND 20:  5150-6150 cm-1 (low - H2O; high - H2O)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K20/      KA(5,13,MG),KB(5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(4,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(65,MG), ABSB(235,MG), SFLUXREF(MG), ABSCH4(MG)

C     Rayleigh extinction coefficient at v = 5670 cm-1.
      DATA RAYL /4.12E-09/

      DATA ABSCH4/
     &     1.01381E-03,6.33692E-03,1.94185E-02,4.83210E-02,
     &     2.36574E-03,6.61973E-04,5.64552E-04,2.83183E-04,
     &     7.43623E-05,8.90159E-07,6.98728E-07,6.51832E-08,
     &     2.96619E-08,0.,0.,0./

      DATA SFLUXREF/
C     Kurucz
     &     9.34081, 8.93720, 8.19346, 7.39196,
     &     6.12127, 5.23956, 4.24941, 3.20013,
     &     2.16047,0.234509,0.194593,0.151512,
     &     0.110315, 7.09959E-02, 2.70573E-02, 3.36042E-03/

      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      LAYREFFR = 3
C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(20) + 1
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(20) + 1
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(20)
            TAUG(LAY,IG) = COLH2O(LAY) * 
     &          ((FAC00(LAY) * ABSA(IND0,IG) +
     &           FAC10(LAY) * ABSA(IND0+1,IG) +
     &           FAC01(LAY) * ABSA(IND1,IG) +
     &           FAC11(LAY) * ABSA(IND1+1,IG)) +
     &           SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
     &           + TAURAY
     &           + COLCH4(LAY) * ABSCH4(IG)
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG) 
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(20) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(20) + 1
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(20)
            TAUG(LAY,IG) = COLH2O(LAY) *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG)))) +
     &           TAURAY +
     &           COLCH4(LAY) * ABSCH4(IG)
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB21


C     BAND 21:  6150-7700 cm-1 (low - H2O,CO2; high - H2O,CO2)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K21/      KA(9,5,13,MG),KB(5,5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(4,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG),ABSB(1175,MG),SFLUXREF(MG,9)

C     Rayleigh extinction coefficient at v = 6925 cm-1.
      DATA RAYL /9.41E-09/

      DATA SFLUXREF/
C     Kurucz
     &     16.1643, 15.5806, 14.7254, 13.5541,
     &     11.9519,10.44410, 8.37884, 6.26384,
     &     4.28435,0.465228,0.385095,0.304226,
     &     0.222479,0.143286, 5.58046E-02, 7.84856E-03,
     &     15.6451, 15.3170, 14.6987, 13.7350,
     &     12.2267,10.51646, 8.47150, 6.38873,
     &     4.33536,0.470610,0.389426,0.306461,
     &     0.223537,0.143273, 5.58179E-02, 7.84856E-03,
     &     15.6092, 15.3293, 14.6881, 13.6693,
     &     12.2342,10.52010, 8.49442, 6.42138,
     &     4.35865,0.473349,0.391349,0.308861,
     &     0.224666,0.144799, 5.58176E-02, 7.84881E-03,
     &     15.5786, 15.3422, 14.6894, 13.6040,
     &     12.2567,10.49400, 8.53521, 6.44427,
     &     4.37208,0.475709,0.392956,0.309737,
     &     0.226274,0.146483, 5.59325E-02, 7.84881E-03,
     &     15.5380, 15.3826, 14.6575, 13.5722,
     &     12.2646,10.47672, 8.57158, 6.46343,
     &     4.38259,0.477647,0.393982,0.310686,
     &     0.227620,0.148376, 5.60398E-02, 7.83925E-03,
     &     15.5124, 15.3986, 14.6240, 13.5535,
     &     12.2468,10.48891, 8.60434, 6.47985,
     &     4.39448,0.478267,0.395618,0.311043,
     &     0.230927,0.148774, 5.61189E-02, 7.83925E-03,
     &     15.4910, 15.4028, 14.5772, 13.5507,
     &     12.2122,10.52735, 8.62650, 6.49644,
     &     4.41173,0.478627,0.396433,0.314199,
     &     0.233125,0.149052, 5.62309E-02, 7.83925E-03,
     &     15.4562, 15.3928, 14.5510, 13.5122,
     &     12.1890, 10.5826, 8.65842, 6.51558,
     &     4.42747,0.480669,0.400143,0.318144,
     &     0.233937,0.149119, 5.62309E-02, 7.83925E-03,
     &     15.0069, 15.1479, 14.7802, 13.6085,
     &     12.2793, 10.6929, 8.72723, 6.57114,
     &     4.46330,0.486724,0.401446,0.318879,
     &     0.233959,0.149119, 5.62309E-02, 7.83925E-03/

      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA,KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT = 0.0045321
      LAYREFFR = 8

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         SPECCOMB = COLH2O(LAY) + STRRAT*COLCO2(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(21) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(21) + JS
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(21)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG)) +
     &           TAURAY +
     &           COLH2O(LAY) * 
     &           (SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG,JS) 
     &           + FS * (SFLUXREF(IG,JS+1) - SFLUXREF(IG,JS))
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         SPECCOMB = COLH2O(LAY) + STRRAT*COLCO2(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 4.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(21) + JS
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(21) + JS
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(21)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSB(IND0,IG) +
     &           FAC100 * ABSB(IND0+1,IG) +
     &           FAC010 * ABSB(IND0+5,IG) +
     &           FAC110 * ABSB(IND0+6,IG) +
     &           FAC001 * ABSB(IND1,IG) + 
     &           FAC101 * ABSB(IND1+1,IG) +
     &           FAC011 * ABSB(IND1+5,IG) +
     &           FAC111 * ABSB(IND1+6,IG)) +
     &           TAURAY +
     &           COLH2O(LAY) * 
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG)))
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END
C----------------------------------------------------------------------------

      SUBROUTINE TAUGB22

C     BAND 22:  7700-8050 cm-1 (low - H2O,O2; high - O2)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K22/      KA(9,5,13,MG),KB(5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(3,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG), ABSB(235,MG), SFLUXREF(MG,9)

C     Rayleigh extinction coefficient at v = 8000 cm-1.
      DATA RAYL /1.54E-08/

      DATA SFLUXREF/
C     Planck
C     Kurucz
     &     3.71641, 3.63190, 3.44795, 3.17936,
     &     2.86071, 2.48490, 2.02471, 1.52475,
     &     1.03811,0.113272, 9.37115E-02, 7.38969E-02,
     &     5.44713E-02, 3.45905E-02, 1.30293E-02, 1.84198E-03,
     &     3.73933, 3.60360, 3.43370, 3.19749,
     &     2.87747, 2.47926, 2.02175, 1.52010,
     &     1.03612,0.113265, 9.37145E-02, 7.38951E-02,
     &     5.44714E-02, 3.45906E-02, 1.30293E-02, 1.84198E-03,
     &     3.73889, 3.60279, 3.43404, 3.20560,
     &     2.87367, 2.47515, 2.02412, 1.52315,
     &     1.03146,0.113272, 9.36707E-02, 7.39080E-02,
     &     5.44598E-02, 3.45906E-02, 1.30293E-02, 1.84198E-03,
     &     3.73801, 3.60530, 3.43659, 3.20640,
     &     2.87039, 2.47330, 2.02428, 1.52509,
     &     1.03037,0.112553, 9.35352E-02, 7.39675E-02,
     &     5.43951E-02, 3.45669E-02, 1.30292E-02, 1.84198E-03,
     &     3.73809, 3.60996, 3.43602, 3.20364,
     &     2.87005, 2.47343, 2.02353, 1.52617,
     &     1.03138,0.111172, 9.29885E-02, 7.35034E-02,
     &     5.42427E-02, 3.45732E-02, 1.30169E-02, 1.84550E-03,
     &     3.73872, 3.62054, 3.42934, 3.20110,
     &     2.86886, 2.47379, 2.02237, 1.52754,
     &     1.03228,0.111597, 9.12252E-02, 7.33115E-02,
     &     5.35600E-02, 3.45187E-02, 1.30184E-02, 1.84551E-03,
     &     3.73969, 3.65461, 3.40646, 3.19082,
     &     2.86919, 2.47289, 2.02312, 1.52629,
     &     1.03329,0.111611, 9.16275E-02, 7.14731E-02,
     &     5.31771E-02, 3.44980E-02, 1.30190E-02, 1.84551E-03,
     &     3.73995, 3.65348, 3.43707, 3.16351,
     &     2.87003, 2.47392, 2.02114, 1.52548,
     &     1.03306,0.111088, 9.12422E-02, 7.11146E-02,
     &     5.31333E-02, 3.45302E-02, 1.30209E-02, 1.84554E-03,
     &     3.73788, 3.65004, 3.46938, 3.15236,
     &     2.86381, 2.47393, 2.01715, 1.52134,
     &     1.03163,0.111259, 9.12948E-02, 7.09999E-02,
     &     5.31792E-02, 3.44955E-02, 1.30189E-02, 1.84551E-03/
      EQUIVALENCE (KA,ABSA),(KB,ABSB)
      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT = 0.022708
      LAYREFFR = 2
C     The following factor is the ratio of total O2 band intensity (lines 
C     and Mate continuum) to O2 band intensity (line only).  It is needed
C     to adjust the optical depths since the k's include only lines.
      O2ADJ = 1.6
C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP

      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         O2CONT = 4.35e-4*colo2(lay)/(350.0*2.0)
         SPECCOMB = COLH2O(LAY) + O2ADJ*STRRAT*COLO2(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
c         ODADJ = SPECPARM + O2ADJ * (1. - SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(22) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(22) + JS
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(22)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG)) +
     &           TAURAY +
     &           COLH2O(LAY) * 
     &           (SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
     &           + O2CONT
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG,JS) 
     &           + FS * (SFLUXREF(IG,JS+1) - SFLUXREF(IG,JS))
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         O2CONT = 4.35e-4*colo2(lay)/(350.0*2.0)
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(22) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(22) + 1
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(22)
            TAUG(LAY,IG) = COLO2(LAY) * O2ADJ *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG)) +
     &           TAURAY
     &           + O2CONT
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END
C----------------------------------------------------------------------------

      SUBROUTINE TAUGB23

C     BAND 23:  8050-12850 cm-1 (low - H2O; high - nothing)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K23/      KA(5,13,MG),SELFREF(10,MG),FORREF(3,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(65,MG), SFLUXREF(MG), RAYL(MG)

      DATA RAYL/
     &     5.94837E-08,5.70593E-08,6.27845E-08,5.56602E-08,
     &     5.25571E-08,4.73388E-08,4.17466E-08,3.98097E-08,
     &     4.00786E-08,3.67478E-08,3.45186E-08,3.46156E-08,
     &     3.32155E-08,3.23642E-08,2.72590E-08,2.96813E-08/
      DATA SFLUXREF/
C     Kurucz
     &     53.2101, 51.4143, 49.3348, 45.4612,
     &     40.8294, 35.1801, 28.6947, 21.5751,
     &     14.6388, 1.59111, 1.31860, 1.04018,
     &     0.762140,0.484214,0.182275, 2.54948E-02/
 
      EQUIVALENCE (KA,ABSA)
      REAL KA
      HVRTAU = '$Revision: 2.5 $'
      LAYREFFR = 6
C     Average Giver et al. correction factor for this band.
      GIVFAC = 1.029

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(23) + 1
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(23) + 1
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         DO 2000 IG = 1, NG(23)
            TAURAY = COLMOL(LAY) * RAYL(IG)
            TAUG(LAY,IG) = COLH2O(LAY) * 
     &          (GIVFAC * (FAC00(LAY) * ABSA(IND0,IG) +
     &           FAC10(LAY) * ABSA(IND0+1,IG) +
     &           FAC01(LAY) * ABSA(IND1,IG) +
     &           FAC11(LAY) * ABSA(IND1+1,IG)) +
     &           SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG)))) +
     &           TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG) 
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         DO 3000 IG = 1, NG(23)
            TAUG(LAY,IG) = COLMOL(LAY) * RAYL(IG)
            SSA(LAY,IG) = 1.0
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END
C----------------------------------------------------------------------------

      SUBROUTINE TAUGB24

C     BAND 24:  12850-16000 cm-1 (low - H2O,O2; high - O2)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K24/      KA(9,5,13,MG),KB(5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(3,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG), ABSB(235,MG), SFLUXREF(MG,9)
      DIMENSION ABSO3A(MG), ABSO3B(MG), RAYLA(MG,9), RAYLB(MG)

      DATA RAYLA/
     &     1.28405E-07,1.45501E-07,1.67272E-07,1.94856E-07,
     &     2.15248E-07,2.34920E-07,2.48558E-07,1.80004E-07,
     &     1.46504E-07,1.31355E-07,1.33562E-07,1.35618E-07,
     &     1.22412E-07,1.19842E-07,1.19924E-07,1.20264E-07,
     &     1.41622E-07,1.93436E-07,2.25057E-07,2.01025E-07,
     &     1.85138E-07,1.72672E-07,1.64771E-07,1.59312E-07,
     &     1.44961E-07,1.37448E-07,1.37506E-07,1.38081E-07,
     &     1.22432E-07,1.19844E-07,1.19921E-07,1.20287E-07,
     &     1.45382E-07,1.97020E-07,2.22781E-07,1.96062E-07,
     &     1.83495E-07,1.72495E-07,1.64910E-07,1.58797E-07,
     &     1.46208E-07,1.42274E-07,1.40445E-07,1.39496E-07,
     &     1.26940E-07,1.19844E-07,1.19921E-07,1.20287E-07,
     &     1.48247E-07,1.99958E-07,2.18048E-07,1.93896E-07,
     &     1.83125E-07,1.73244E-07,1.64320E-07,1.58298E-07,
     &     1.48428E-07,1.44769E-07,1.43704E-07,1.38498E-07,
     &     1.31732E-07,1.22299E-07,1.19921E-07,1.20287E-07,
     &     1.51343E-07,1.99621E-07,2.14563E-07,1.93824E-07,
     &     1.82992E-07,1.73143E-07,1.64587E-07,1.57355E-07,
     &     1.51198E-07,1.46373E-07,1.45438E-07,1.38095E-07,
     &     1.35026E-07,1.27504E-07,1.19921E-07,1.20287E-07,
     &     1.54462E-07,1.97610E-07,2.11992E-07,1.93831E-07,
     &     1.83900E-07,1.73125E-07,1.64093E-07,1.57651E-07,
     &     1.53158E-07,1.46843E-07,1.44733E-07,1.40611E-07,
     &     1.37320E-07,1.33932E-07,1.20423E-07,1.20287E-07,
     &     1.59068E-07,1.92757E-07,2.09865E-07,1.95132E-07,
     &     1.83641E-07,1.73778E-07,1.63215E-07,1.59462E-07,
     &     1.54331E-07,1.46177E-07,1.45819E-07,1.43177E-07,
     &     1.39797E-07,1.36780E-07,1.33385E-07,1.20287E-07,
     &     1.62066E-07,1.87529E-07,2.07191E-07,1.97788E-07,
     &     1.84920E-07,1.72951E-07,1.65450E-07,1.60344E-07,
     &     1.54403E-07,1.47679E-07,1.47287E-07,1.44951E-07,
     &     1.42517E-07,1.41107E-07,1.48688E-07,1.51127E-07,
     &     1.19177E-07,1.86522E-07,2.20324E-07,2.13543E-07,
     &     1.92198E-07,1.81641E-07,1.70092E-07,1.65072E-07,
     &     1.59804E-07,1.56745E-07,1.51235E-07,1.51400E-07,
     &     1.49635E-07,1.48056E-07,1.49046E-07,1.51010E-07/
      DATA RAYLB/
     &     1.23766E-07,1.40524E-07,1.61610E-07,1.83232E-07,
     &     2.02951E-07,2.21367E-07,2.38367E-07,2.53019E-07,
     &     2.12202E-07,1.36977E-07,1.39118E-07,1.37097E-07,
     &     1.33223E-07,1.38695E-07,1.19868E-07,1.20062E-07/

      DATA SFLUXREF/
C     Kurucz
     &     34.3610, 33.1240, 31.3948, 28.7248,
     &     24.7884, 21.4892, 17.3972, 13.7928,
     &     9.54462, 1.05002,0.867332,0.685753,
     &     0.504718,0.323112,0.122183, 1.70288E-02,
     &     34.2367, 32.4327, 30.0863, 28.2085,
     &     25.6533, 22.3412, 18.3112, 13.8521,
     &     9.51035, 1.04138,0.863493,0.682790,
     &     0.504721,0.323102,0.122193, 1.70288E-02,
     &     34.1883, 32.2479, 30.2650, 28.2914,
     &     25.6626, 22.3163, 18.3327, 13.8508,
     &     9.49190, 1.03672,0.858272,0.681485,
     &     0.501363,0.323110,0.122183, 1.70288E-02,
     &     34.1365, 32.2316, 30.3325, 28.3305,
     &     25.6420, 22.3223, 18.3411, 13.8471,
     &     9.47492, 1.03376,0.855380,0.679085,
     &     0.497998,0.323053,0.122183, 1.70288E-02,
     &     34.0460, 32.2795, 30.4147, 28.3123,
     &     25.6438, 22.3238, 18.3441, 13.8528,
     &     9.45222, 1.03058,0.854037,0.675554,
     &     0.498344,0.320072,0.122193, 1.70288E-02,
     &     33.9909, 32.3127, 30.4854, 28.3005,
     &     25.6310, 22.3294, 18.3459, 13.8488,
     &     9.43336, 1.02901,0.852728,0.672322,
     &     0.498056,0.317753,0.122183, 1.70288E-02,
     &     33.9225, 32.4097, 30.5125, 28.2810,
     &     25.6387, 22.3080, 18.3715, 13.8248,
     &     9.41834, 1.02735,0.850807,0.671379,
     &     0.496975,0.317158,0.119297, 1.70207E-02,
     &     33.8940, 32.4951, 30.5494, 28.2788,
     &     25.5975, 22.3225, 18.3358, 13.8199,
     &     9.40283, 1.02751,0.850729,0.670152,
     &     0.494294,0.315829,0.116195, 1.64138E-02,
     &     34.6501, 32.6690, 30.2872, 28.0955,
     &     25.4662, 22.1446, 18.2754, 13.7573,
     &     9.36645, 1.02356,0.847154,0.668519,
     &     0.489186,0.313790,0.117074, 1.60943E-02/

      DATA ABSO3A/
     &     8.03067E-02,0.180926,0.227484,0.168015,
     &     0.138284,0.114537,9.50114E-02,8.06816E-02,
     &     6.76406E-02,5.69802E-02,5.63283E-02,4.57592E-02,
     &     4.21862E-02,3.47949E-02,2.65731E-02,2.67628E-02/
      DATA ABSO3B/
     &     2.94848E-02,4.33642E-02,6.70197E-02,0.104990,
     &     0.156180,0.214638,0.266281,0.317941,
     &     0.355327,0.371241,0.374396,0.326847,
     &     0.126497,6.95264E-02,2.58175E-02,2.52862E-02/
 
      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT = 0.124692
      LAYREFFR = 1

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         SPECCOMB = COLH2O(LAY) + STRRAT*COLO2(LAY)
         SPECPARM = COLH2O(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(24) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(24) + JS
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         DO 2000 IG = 1, NG(24)
            TAURAY = COLMOL(LAY) * (RAYLA(IG,JS) +
     &           FS * (RAYLA(IG,JS+1) - RAYLA(IG,JS)))
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG)) +
     &           COLO3(LAY) * ABSO3A(IG) +
     &           TAURAY +
     &           COLH2O(LAY) * 
     &           (SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG,JS) 
     &           + FS * (SFLUXREF(IG,JS+1) - SFLUXREF(IG,JS))
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(24) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(24) + 1
         DO 3000 IG = 1, NG(24)
            TAURAY = COLMOL(LAY) * RAYLB(IG)
            TAUG(LAY,IG) = COLO2(LAY) *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG)) +
     &           COLO3(LAY) * ABSO3B(IG) +
     &           TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB25

C     BAND 25:  16000-22650 cm-1 (low - H2O; high - nothing)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /K25/      KA(5,13,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(65,MG), SFLUXREF(MG),RAYL(MG)
      DIMENSION ABSO3A(MG), ABSO3B(MG)

      DATA RAYL/
     &     9.81132E-07,8.25605E-07,6.71302E-07,5.53556E-07,
     &     3.97383E-07,3.68206E-07,4.42379E-07,4.57799E-07,
     &     4.22683E-07,3.87113E-07,3.79810E-07,3.63192E-07,
     &     3.51921E-07,3.34231E-07,3.34294E-07,3.32673E-07/
      DATA SFLUXREF/
c     Kurucz
     &     42.6858, 45.7720, 44.9872, 45.9662,
     &     46.5458, 41.6926, 32.2893, 24.0928,
     &     16.7686, 1.86048, 1.54057, 1.23503,
     &     0.915085,0.590099,0.218622, 3.21287E-02/

      DATA ABSO3A/
     &     2.32664E-02,5.76154E-02,0.125389,0.250158,
     &     0.378756,0.402196,0.352026,0.352036,
     &     0.386253,0.414598,0.420079,0.435471,
     &     0.445487,0.459549,0.452920,0.456838/
      DATA ABSO3B/
     &     1.76917E-02,4.64185E-02,1.03640E-01,0.189469,
     &     0.303858,0.400248,0.447357,0.470009,
     &     0.498673,0.515696,0.517053,0.517930,
     &     0.518345,0.524952,0.508244,0.468981/
 
      EQUIVALENCE (KA,ABSA)

      REAL KA
      HVRTAU = '$Revision: 2.5 $'
      LAYREFFR = 2

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         IF (JP(LAY) .LT. LAYREFFR .AND. JP(LAY+1) .GE. LAYREFFR) 
     &        LAYSOLFR = MIN(LAY+1,LAYTROP)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(25) + 1
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(25) + 1
         DO 2000 IG = 1, NG(25)
            TAURAY = COLMOL(LAY) * RAYL(IG)
            TAUG(LAY,IG) = COLH2O(LAY) * 
     &          (FAC00(LAY) * ABSA(IND0,IG) +
     &           FAC10(LAY) * ABSA(IND0+1,IG) +
     &           FAC01(LAY) * ABSA(IND1,IG) +
     &           FAC11(LAY) * ABSA(IND1+1,IG)) +
     &           COLO3(LAY) * ABSO3A(IG) +
     &           TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG) 
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         DO 3000 IG = 1, NG(25)
            TAURAY = COLMOL(LAY) * RAYL(IG)
            TAUG(LAY,IG) = COLO3(LAY) * ABSO3B(IG) +
     &           TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB26

C     BAND 26:  22650-29000 cm-1 (low - nothing; high - nothing)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU


      DIMENSION SFLUXREF(MG),RAYL(MG)

      DATA RAYL/
     &     1.21263E-06,1.43428E-06,1.67677E-06,1.93255E-06,
     &     2.19177E-06,2.44195E-06,2.66926E-06,2.85990E-06,
     &     3.00380E-06,3.06996E-06,3.08184E-06,3.09172E-06,
     &     3.09938E-06,3.10456E-06,3.10727E-06,3.10818E-06/
C     Kurucz
      DATA SFLUXREF/ 
c     &     129.462, 15*0.0/
     &     29.0079,28.4088,20.3099,13.0283,
     &     11.8619,9.95840,6.68696,5.38987,
     &     3.49829,0.407693,0.299027,0.236827,
     &     0.188502,0.163489,4.64335E-02,2.72662E-03/

      HVRTAU = '$Revision: 2.5 $' 
C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      LAYSOLFR = LAYTROP
      DO 2500 LAY = 1, LAYTROP
         DO 2000 IG = 1, NG(26)
            TAUG(LAY,IG) = COLMOL(LAY) * RAYL(IG)
            SSA(LAY,IG) = 1.0
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG) 
 2000    CONTINUE
 2500 CONTINUE

      DO 3500 LAY = LAYTROP+1, NLAYERS
         DO 3000 IG = 1, NG(26)
            TAUG(LAY,IG) = COLMOL(LAY) * RAYL(IG)
            SSA(LAY,IG) = 1.0
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB27

C     BAND 27:  29000-38000 cm-1 (low - O3; high - O3)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K27/      KA(5,13,MG),KB(5,13:59,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU


      DIMENSION ABSA(65,MG), ABSB(235,MG), SFLUXREF(MG)
      DIMENSION RAYL(MG)

      DATA RAYL/
     &     3.44534E-06,4.14480E-06,4.95069E-06,5.81204E-06,
     &     6.69748E-06,7.56488E-06,8.36344E-06,9.04135E-06,
     &     9.58324E-06,9.81542E-06,9.75119E-06,9.74533E-06,
     &     9.74139E-06,9.73525E-06,9.73577E-06,9.73618E-06/
      DATA SFLUXREF/
C     The following values were obtained using the "low resolution"
C     version of the Kurucz solar source function.  For unknown reasons,
C     the total irradiance in this band differs from the corresponding
C     total in the "high-resolution" version of the Kurucz function.
C     Therefore, below these values are scaled by the factor SCALEKUR.
C     Kurucz
     &     14.0526, 11.4794, 8.72590, 5.56966,
     &     3.80927, 1.57690, 1.15099, 1.10012,
     &     0.658212, 5.86859E-02, 5.56186E-02, 4.68040E-02,
     &     3.64897E-02, 3.58053E-02, 1.38130E-02, 1.90193E-03/

      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      LAYREFFR = 32
      SCALEKUR = 50.15/48.37

C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  
      DO 2500 LAY = 1, LAYTROP
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(27) + 1
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(27) + 1
         DO 2000 IG = 1, NG(27)
            TAURAY = COLMOL(LAY) * RAYL(IG)
            TAUG(LAY,IG) = COLO3(LAY) * 
     &          (FAC00(LAY) * ABSA(IND0,IG) +
     &           FAC10(LAY) * ABSA(IND0+1,IG) +
     &           FAC01(LAY) * ABSA(IND1,IG) +
     &           FAC11(LAY) * ABSA(IND1+1,IG)) +
     &           TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 2000    CONTINUE
 2500 CONTINUE

      LAYSOLFR = NLAYERS
      DO 3500 LAY = LAYTROP+1, NLAYERS
         IF (JP(LAY-1) .LT. LAYREFFR .AND. JP(LAY) .GE. LAYREFFR) 
     &        LAYSOLFR = LAY
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(27) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(27) + 1
         DO 3000 IG = 1, NG(27)
            TAURAY = COLMOL(LAY) * RAYL(IG)
            TAUG(LAY,IG) = COLO3(LAY) *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG)) +
     &           TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY.EQ.LAYSOLFR) SFLUXZEN(IG) = SCALEKUR * SFLUXREF(IG) 
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB28

C     BAND 28:  38000-50000 cm-1 (low - O3,O2; high - O3,O2)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K28/      KA(9,5,13,MG),KB(5,5,13:59,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(585,MG), ABSB(1175,MG), SFLUXREF(MG,5)
      data rayl /2.02e-5/
      DATA SFLUXREF/
C     Kurucz
     &     1.06156,0.599910,0.422462,0.400077,
     &     0.282221,0.187893, 6.77357E-02, 3.04572E-02,
     &     2.00442E-02, 2.30786E-03, 2.08824E-03, 1.42604E-03,
     &     9.67384E-04, 6.35362E-04, 1.47727E-04, 6.87639E-06,
     &     1.07598,0.585099,0.422852,0.400077,
     &     0.282221,0.187893, 6.69686E-02, 3.09070E-02,
     &     2.02400E-02, 2.47760E-03, 1.89411E-03, 1.41122E-03,
     &     1.12449E-03, 5.73505E-04, 2.04160E-04, 1.58371E-05,
     &     0.461647,0.406113,0.332506,0.307508,
     &     0.211167,0.235457,0.495886,0.363921,
     &     0.192700, 2.04678E-02, 1.55407E-02, 1.03882E-02,
     &     1.10778E-02, 1.00504E-02, 4.93497E-03, 5.73410E-04,
     &     0.132669,0.175058,0.359263,0.388142,
     &     0.350359,0.475892,0.489593,0.408437,
     &     0.221049, 1.94514E-02, 1.54848E-02, 1.44999E-02,
     &     1.44568E-02, 1.00527E-02, 4.95897E-03, 5.73327E-04,
     &     7.54800E-02,0.232246,0.359263,0.388142,
     &     0.350359,0.426317,0.493485,0.432016,
     &     0.239203, 1.74951E-02, 1.74477E-02, 1.83566E-02,
     &     1.44818E-02, 1.01048E-02, 4.97487E-03, 5.66831E-04/
      EQUIVALENCE (KA,ABSA),(KB,ABSB)
      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      STRRAT = 6.67029E-7
      LAYREFFR = 58
C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  

      DO 2500 LAY = 1, LAYTROP
         SPECCOMB = COLO3(LAY) + STRRAT*COLO2(LAY)
         SPECPARM = COLO3(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 8.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(28) + JS
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(28) + JS
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(28)
            TAUG(LAY,IG) = SPECCOMB * 
     &          (FAC000 * ABSA(IND0,IG) +
     &           FAC100 * ABSA(IND0+1,IG) +
     &           FAC010 * ABSA(IND0+9,IG) +
     &           FAC110 * ABSA(IND0+10,IG) +
     &           FAC001 * ABSA(IND1,IG) + 
     &           FAC101 * ABSA(IND1+1,IG) +
     &           FAC011 * ABSA(IND1+9,IG) +
     &           FAC111 * ABSA(IND1+10,IG))
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 2000    CONTINUE
 2500 CONTINUE

      LAYSOLFR = NLAYERS
      DO 3500 LAY = LAYTROP+1, NLAYERS
         IF (JP(LAY-1) .LT. LAYREFFR .AND. JP(LAY) .GE. LAYREFFR) 
     &        LAYSOLFR = LAY
         SPECCOMB = COLO3(LAY) + STRRAT*COLO2(LAY)
         SPECPARM = COLO3(LAY)/SPECCOMB 
         IF (SPECPARM .GE. ONEMINUS) SPECPARM = ONEMINUS
         SPECMULT = 4.*(SPECPARM)
         JS = 1 + INT(SPECMULT)
         FS = AMOD(SPECMULT,1.0)
         FAC000 = (1. - FS) * FAC00(LAY)
         FAC010 = (1. - FS) * FAC10(LAY)
         FAC100 = FS * FAC00(LAY)
         FAC110 = FS * FAC10(LAY)
         FAC001 = (1. - FS) * FAC01(LAY)
         FAC011 = (1. - FS) * FAC11(LAY)
         FAC101 = FS * FAC01(LAY)
         FAC111 = FS * FAC11(LAY)
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(28) + JS
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(28) + JS
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(28)
            TAUG(LAY,IG) = SPECCOMB *
     &          (FAC000 * ABSB(IND0,IG) +
     &           FAC100 * ABSB(IND0+1,IG) +
     &           FAC010 * ABSB(IND0+5,IG) +
     &           FAC110 * ABSB(IND0+6,IG) +
     &           FAC001 * ABSB(IND1,IG) + 
     &           FAC101 * ABSB(IND1+1,IG) +
     &           FAC011 * ABSB(IND1+5,IG) +
     &           FAC111 * ABSB(IND1+6,IG)) 
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG,JS) 
     &           + FS * (SFLUXREF(IG,JS+1) - SFLUXREF(IG,JS))
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END

C----------------------------------------------------------------------------

      SUBROUTINE TAUGB29

C     BAND 29:  820-2600 cm-1 (low - H2O; high - CO2)

      PARAMETER (MG=16, MXLAY=203, NBANDS=14, MXMOL=38)

C  Output

      COMMON /TAUGCOM/  TAUG(MXLAY,MG)
      COMMON /SSAGCOM/  SSA(MXLAY,MG)
      COMMON /SOLARIN/  SFLUXZEN(MG)

C  Input

      COMMON /FEATURES/ NG(16:15+NBANDS),NSPA(16:15+NBANDS),
     &                  NSPB(16:15+NBANDS)
      COMMON /PRECISE/  ONEMINUS
      COMMON /PROFILE/  NLAYERS,PAVEL(MXLAY),TAVEL(MXLAY),
     &                  PZ(0:MXLAY),TZ(0:MXLAY),TBOUND
      COMMON /SPECIES/  COLDRY(MXLAY),WKL(MXMOL,MXLAY),WBRODL(MXLAY),
     &                  COLMOL(MXLAY),NMOL
      COMMON /PROFDATA/ LAYTROP,LAYSWTCH,LAYLOW,
     &                  COLH2O(MXLAY),COLCO2(MXLAY),
     &                  COLO3(MXLAY),COLN2O(MXLAY),COLCH4(MXLAY),
     &                  COLO2(MXLAY),CO2MULT(MXLAY)
      COMMON /INTFAC/   FAC00(MXLAY),FAC01(MXLAY),                            
     &                  FAC10(MXLAY),FAC11(MXLAY)                             
      COMMON /INTIND/   JP(MXLAY),JT(MXLAY),JT1(MXLAY)
      COMMON /SELF/     SELFFAC(MXLAY), SELFFRAC(MXLAY), INDSELF(MXLAY)
      COMMON /FOREIGN/  FORFAC(MXLAY), FORFRAC(MXLAY), INDFOR(MXLAY)
      COMMON /K29/      KA(5,13,MG),KB(5,13:59,MG),SELFREF(10,MG),
     &                  FORREF(4,MG)

      COMMON /CVRTAU/   HNAMTAU,HVRTAU

      CHARACTER*18      HNAMTAU,HVRTAU

      DIMENSION ABSA(65,MG), ABSB(235,MG), SFLUXREF(MG)
      DIMENSION ABSH2O(MG), ABSCO2(MG)

C     Rayleigh extinction coefficient at v = 2200 cm-1.
      DATA RAYL /9.30E-11/

      DATA ABSCO2/
     &     2.90073E-06, 2.12382E-05, 1.03032E-04, 1.86481E-04,
     &     4.31997E-04, 6.08238E-04, 2.17603E-03, 4.64479E-02,
     &     2.96956, 14.9569, 28.4831, 61.3998,
     &     164.129, 832.282, 4995.02, 12678.1/
      DATA ABSH2O/
     &     2.99508E-04, 3.95012E-03, 1.49316E-02, 3.24384E-02,
     &     6.92879E-02, 0.123523, 0.360985, 1.86434,
     &     10.38157, 0.214129, 0.213914, 0.212781,
     &     0.215562, 0.218087, 0.220918, 0.218546/

      DATA SFLUXREF/
     &     1.32880, 2.14018, 1.97612, 1.79000,
     &     1.51242, 1.22977, 1.06052, 0.800996,
     &     0.748053, 8.64369E-02, 7.10675E-02, 5.62425E-02,
     &     4.46988E-02, 3.07441E-02, 1.16728E-02, 1.65573E-03/
      EQUIVALENCE (KA,ABSA),(KB,ABSB)

      REAL KA, KB
      HVRTAU = '$Revision: 2.5 $'
      LAYREFFR = 49
C     Compute the optical depth by interpolating in ln(pressure), 
C     temperature, and appropriate species.  Below LAYTROP, the water
C     vapor self-continuum is interpolated (in temperature) separately.  

      DO 2500 LAY = 1, LAYTROP
         IND0 = ((JP(LAY)-1)*5+(JT(LAY)-1))*NSPA(29) + 1
         IND1 = (JP(LAY)*5+(JT1(LAY)-1))*NSPA(29) + 1
         INDS = INDSELF(LAY)
         INDF = INDFOR(LAY)
         TAURAY = COLMOL(LAY) * RAYL
         DO 2000 IG = 1, NG(29)
            TAUG(LAY,IG) = COLH2O(LAY) * 
     &          ((FAC00(LAY) * ABSA(IND0,IG) +
     &           FAC10(LAY) * ABSA(IND0+1,IG) +
     &           FAC01(LAY) * ABSA(IND1,IG) +
     &           FAC11(LAY) * ABSA(IND1+1,IG)) +
     &           SELFFAC(LAY) * (SELFREF(INDS,IG) + 
     &           SELFFRAC(LAY) *
     &           (SELFREF(INDS+1,IG) - SELFREF(INDS,IG))) +
     &           FORFAC(LAY) * (FORREF(INDF,IG) + 
     &           FORFRAC(LAY) *
     &           (FORREF(INDF+1,IG) - FORREF(INDF,IG))))
     &           + TAURAY
     &           + COLCO2(LAY) * ABSCO2(IG)
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
 2000    CONTINUE
 2500 CONTINUE

      LAYSOLFR = NLAYERS
      DO 3500 LAY = LAYTROP+1, NLAYERS
         IF (JP(LAY-1) .LT. LAYREFFR .AND. JP(LAY) .GE. LAYREFFR) 
     &        LAYSOLFR = LAY
         IND0 = ((JP(LAY)-13)*5+(JT(LAY)-1))*NSPB(29) + 1
         IND1 = ((JP(LAY)-12)*5+(JT1(LAY)-1))*NSPB(29) + 1
         TAURAY = COLMOL(LAY) * RAYL
         DO 3000 IG = 1, NG(29)
            TAUG(LAY,IG) = COLCO2(LAY) *
     &          (FAC00(LAY) * ABSB(IND0,IG) +
     &           FAC10(LAY) * ABSB(IND0+1,IG) +
     &           FAC01(LAY) * ABSB(IND1,IG) + 
     &           FAC11(LAY) * ABSB(IND1+1,IG)) 
     &           + COLH2O(LAY) * ABSH2O(IG)
     &           + TAURAY
            SSA(LAY,IG) = TAURAY/TAUG(LAY,IG)
            IF (LAY .EQ. LAYSOLFR) SFLUXZEN(IG) = SFLUXREF(IG) 
 3000    CONTINUE
 3500 CONTINUE

      RETURN
      END
