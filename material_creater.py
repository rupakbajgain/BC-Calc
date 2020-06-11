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
    if GI=='MM':
        GI='SM'
    return GI

def get_correctedN(SPT_N):
    N60 = 0.55 * 1 * 1 * 0.75 * SPT_N/0.6
    NC = 15+1/2*(SPT_N-15)
    return (N60,NC)

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
    #guess from first letter if it is cohesive or not
    Cu=0
    if is_clayey:
        Cu = 0.29 * N60**0.72 * 100
        Cu=clamp(Cu, 10, 103)
    if GI=='CG' or GI=='GC':
        Cu=20
    elif 'SM'== GI:
        Cu=clamp(Cu,20,50)
    elif 'SC'== GI:
        Cu=clamp(Cu,5,75)
    # But max value of Cu is 2 + pi
    Cu=clamp(Cu,0.01,103)
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
        if packing_case==1:
            phi = clamp(phi,0,30)
        elif packing_case==2:
            phi = clamp(phi,30,35)
        elif packing_case==3:
            phi = clamp(phi,35,40)
        elif packing_case==4:
            phi = clamp(phi,40,45)
        else:
            phi = clamp(phi,45,60)
    else:
        phi=0.01
    return phi

def get_E(N60, GI, packing_case):
    E=10*N60*100
    if GI[0] == 'S':
        if packing_case<2:
            E=clamp(E, 4_000, 10_000)
        elif packing_case==2:
            E=clamp(E, 10_000, 30_000)
        else:
            E=clamp(E, 30_000, 55_000)
    elif GI[0] == 'G':
        E=clamp(E,70_000,170_000)
    elif GI[0] == 'M':
        E=clamp(E,10_000,20_000)
    else:
        if packing_case<3:
            E=clamp(E, 4_000, 20_000)
        else:#elif packing_case<2:
            E=clamp(E, 20_000, 40_000)
        #else: #no stiff clay
        #    E=clamp(E, 40_000, 100_000)
    return E

def get_material(info):
    GI = info[1]
    SPT_N = float(info[2])
    y_sat = float(info[3])
    # now determine properties by various corrections
    GI = GI_correction(GI)
    N60,NC = get_correctedN(SPT_N)
    is_clayey = not (GI[0] in ['S','G'] or GI[1] in ['M','C'])
    gamma = get_correctedGamma(N60, y_sat, GI)
    Cu = get_Cu(N60, GI, is_clayey)
    packing_case = get_packing_state(NC)
    phi = get_phi(N60, GI, packing_case)
    nu = 0.3
    E = get_E(N60, GI, packing_case)
    return (info[0],GI,phi, E, Cu, gamma, nu, N60)

def process_sfile(file):
    input_datas = file
    results = []
    for i in input_datas[1][1]:
        results.append(get_material(i))
    return results

def material_creater(excel_data):
    results = []
    for i in excel_data:
        results.append(process_sfile(i))
    return results

#files = helper.getMyFiles('ped', '.')#.mtl
#for i in files:
#    print('Loading file:', i[0])
#    helper.give_file_hint(i[0])
#    try:
#        process_file(i)
#    except helper.helper_exception:
#        pass
#helper.print_failed()