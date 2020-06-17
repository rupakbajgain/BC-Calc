# imports
import helper
import math

############### Where to place silt is some what clay for now.
## but peat posses none strength

# clamp result between min and max values
def clamp(v, amin, amax):
    if v<amin:
        return amin
    if v>amax:
        return amax
    return v

def GI_correction(GI):
    if not GI[0] in ['S','M','G','C','P','O']:
        GI=GI[1]+GI[1]
    return GI

def get_correctedN(SPT_N, overburden):
    N60 = 0.55 * 1 * 1 * 0.75 * SPT_N/0.6
    return N60

#from some useful notetion paper
def get_correctedGamma(N60, y_sat, GI):
    gamma = y_sat
    if GI[0] in ['G', 'S']:
        if y_sat==0:
            gamma = 16 + 0.1 * N60
    else:
        if y_sat==0:
            gamma = 16.8 + 0.15*N60
    gamma=clamp(gamma,10,2.8*9.81)
    return(gamma)

# correction from: https://civilengineeringbible.com/subtopics.php?i=91
def get_Cu(N60, GI, is_clayey):
    Cu=0
    if is_clayey:
        Cu = 0.29 * N60**0.72 * 100
        Cu=clamp(Cu, 10, 103)
    if GI=='CG' or GI=='GC':
        Cu=clamp(Cu, 20, 25)
    elif 'SM'== GI:
        Cu=clamp(Cu,20,50)
    elif 'SC'== GI:
        Cu=clamp(Cu,5,75)
    Cu=clamp(Cu,0.21,103)#0.2 min plasix
    # Plasix calculation needs very small Cu
    return(Cu)

def get_packing_state(NC):
    # Ok, first determining packing condition as per Table 2.4,
    S_PHELP = [0,4,10,30,50]
    packing_case = 5 # Packing cases as per table
    for i,v in enumerate(S_PHELP):
        if NC>v:
            packing_case=i
    return packing_case

def get_phi(N60, GI, packing_case):
    phi = 27.1 + 0.3*N60 - 0.00054* N60* N60
    if GI[0]=='G':
        if GI[1]=='W':
            phi=clamp(phi, 33, 40)
        else:
            phi=clamp(phi, 32, 44)
    elif GI[0]=='S':
        if packing_case<=1:
            phi = clamp(phi,0,35)
        elif packing_case==2:
            phi = clamp(phi,25,40)
        elif packing_case==3:
            phi = clamp(phi,30,45)
        elif packing_case==4:
            phi = clamp(phi,35,40)
        else:
            phi = clamp(phi,40,60)
    elif GI[0]=='C':
        if GI[1]=='H':
            phi = clamp(phi, 17, 31)
        else:
            phi = clamp(phi, 27, 35)
    else:
        phi = clamp(phi, 23, 41)
    return phi

def get_interpolated_clamped(x, x1, x2, y1, y2):
    x = clamp(x, x1, x2)
    m = (y2-y1)/2
    y1 = y1+m/2
    y2 = y2-m/2#take values from mid
    out = y1 + (y2-y1)/(x2-x1) * (x-x1)
    return out

def get_E_help(N60, GI, surcharge):
    E=10*N60*100
    if GI[0]=='C':
        E = get_interpolated_clamped(N60,1,50,10,100)*surcharge
    elif GI[0]=='S':
        E = get_interpolated_clamped(N60,1,50,50,500)*surcharge
    elif GI[0]=='M':
        E = get_interpolated_clamped(N60,1,50,25,125)*surcharge
    elif GI[0]=='P':
        E = get_interpolated_clamped(N60,1,50,2,25)*surcharge
    return E

def get_E(N60, GI, packing_case, surcharge):#added surcharge
    # packing case is for correction
    E=get_E_help(N60, GI, surcharge)# let's replace it by new formula
    if GI[0] == 'S':
        #if packing_case<=1:
        #    E=clamp(E, 2_000, 15_000)
        #elif packing_case==2:
        #    E=clamp(E, 7_000, 40_000)
        #else:
        #    E=clamp(E, 30_000, 75_000)
        E = clamp(E, 2_000, 75_000)
        # no mixing
    elif GI[0] == 'G':
        E=clamp(E,70_000,170_000)
    elif GI[0]=='C':
        E=clamp(E,4_000,100_000)
    elif GI[0]=='M':
        E=clamp(E,4_000,30_000)
    else:
        #others make it weak
        if packing_case<=2:
            E=clamp(E, 2_000, 10_000)
        else:
            E=clamp(E, 10_000, 20_000)
    return E

def get_material(info, prev_surcharge, depth):
    GI = info[1]
    SPT_N = float(info[2])
    y_sat = float(info[3])
    # now determine properties by various corrections
    GI = GI_correction(GI)
    N60 = get_correctedN(SPT_N, prev_surcharge+17*depth)#guess
    is_clayey = not (GI[0] in ['S','G'])
    gamma = get_correctedGamma(N60, y_sat, GI)
    a_surcharge = prev_surcharge + gamma*depth
    Cu = get_Cu(N60, GI, is_clayey)
    packing_case = get_packing_state(N60)
    phi = get_phi(N60, GI, packing_case)
    nu = 0.3
    E = get_E(N60, GI, packing_case, a_surcharge)
    # c=Cu/2
    return (info[0],GI,phi, E, Cu/2, gamma, nu, N60, a_surcharge)

def process_sfile(file):
    input_datas = file
    results = []
    #surcharge is property of material
    surcharge = 0.
    prev_depth = 0.
    for i in input_datas[1][1]:
        new_depth = float(i[0])
        mat = get_material(i, surcharge, new_depth-prev_depth)
        surcharge = mat[8]
        prev_depth = new_depth
        results.append(mat)
    return results

def material_creater(excel_data):
    results = []
    for i in excel_data:
        results.append(process_sfile(i))
    return results
