# imports
import helper
import math
import subprocess, time
import win32gui
import win32con
import shutil, os
import pyodbc
import pyautogui

calc_depths = [1.5, 3., 4.5]

def get_top_material(input_datas, depth):
    old_material = input_datas[0]
    for i in input_datas:
        deptht,_,_,_,_,_,_,_ = i
        if deptht>depth:
            break
        old_material = i
    return old_material

#For terzaghi
t_tables={}
t_tables['phi']=[0,5,10,15,20,25,30,35,40,45,50]
t_tables['nc']=[5.7,7.3,9.6,12.9,17.7,25.1,37.2,57.8,95.7,172.3,347.5]
t_tables['nq']=[1,1.6,2.7,4.4,7.4,12.7,22.5,41.4,81.3,173.3,415.1]
t_tables['ny']=[0,0.5,1.2,2.5,5,9.7,19.7,42.4,100.4,297.5,1153.0]
#For Mayhoff
m_tables={}
m_tables['phi'] = [0,5,10,15,20,25,26,28,30,32,34,36,38,40,45,50]
m_tables['nc'] = [5.14, 6.49, 8.34, 10.97, 14.83, 20.71, 22.25, 25.79, 30.13, 35.47, 42.14, 50.55, 61.31, 72.25, 133.73, 266.50]
m_tables['nq'] = [1,1.6,2.5,3.9,6.4,10.7,11.8,14.7,18.4,23.2,29.4,37.7,48.9,64.1, 134.7,318.50]
m_tables['ny(m)'] = [0, 0.1, 0.4, 1.1,2.9,6.8,7.9,10.9,15.1,20.8,28.7,40.0,56.1,79.4,200.5,567.4]
m_tables['ny(h)'] = [0,0.1,0.4,1.1,2.9,6.8,7.9,10.9,15.1,20.8,28.7,40.0,56.1,79.4,200.5,567.4]
m_tables['ny(v)'] = [0.0, 0.4, 1.2, 2.6, 5.4, 10.9, 12.5, 16.7, 22.4, 30.2, 41.0, 56.2, 77.9, 109.4, 271.3, 762.84]
def getTable(tables, var, phi):
    if phi>=50:
        return tables[var][15]
    #First find phi index
    idx=0
    while(True):
        if tables['phi'][idx]>phi:
            break
        idx+=1
    if(tables['phi'][idx-1]==phi):
        return tables[var][idx-1]
    else:
        #Let's interpolate
        return (tables[var][idx]-tables[var][idx-1])/(tables['phi'][idx]-tables['phi'][idx-1])*(phi-tables['phi'][idx-1])+tables[var][idx-1]
    
def terzagi_method(phi, gamma, Cu, calc_depth):
    is_cohesive = phi<=0.1
    Nq = getTable(t_tables, 'nq', phi)
    Nc = getTable(t_tables, 'nc', phi)
    Ny = getTable(t_tables, 'ny', phi)
    # Now shape factors , 2x2 foundation
    B = 2
    L = 2
    q = calc_depth * gamma
    c_term = 1.3* Cu*Nc
    q_term = q*Nq
    y_term = 0.4 * gamma * B * Ny
    if is_cohesive:
        y_term= 0.
    p = c_term + q_term + y_term
    #print(c_term,q_term,y_term)
    #print(mat)
    return(p/3)

#all three methods
def meyerhof_method(phi, gamma, Cu, calc_depth):
    is_cohesive = phi<=0.1
    Nq = getTable(m_tables, 'nq', phi)
    Nc = getTable(m_tables, 'nc', phi)
    Ny = getTable(m_tables, 'ny(m)', phi)
    # Now shape factors , 2x2 foundation
    B = 2
    L = 2
    #shape corrections
    Kp = math.tan((45+phi/2)*math.pi/180)**2
    sc=1+0.2*Kp*B/L
    sq=1
    if phi>10:
        sq=1+0.1*Kp*B/L
    sy=sq
    #depth corrections
    dc = 1 +0.2*math.sqrt(Kp)*calc_depth/B
    dq = 1 +0.1*math.sqrt(Kp)*calc_depth/B
    dy=dq
    q = calc_depth * gamma
    c_term = Cu*Nc*sc*dc
    q_term = q*Nq*sq*dq
    y_term = 0.5 * gamma * B * Ny*sy*dy
    if is_cohesive:
        y_term= 0.
    p = c_term + q_term + y_term
    #print(c_term,q_term,y_term)
    #print(mat)
    return(p/3)

def hansen_method(phi, gamma, Cu, calc_depth):
    is_cohesive = phi<=0.1
    Nq = getTable(m_tables, 'nq', phi)
    Nc = getTable(m_tables, 'nc', phi)
    Ny = getTable(m_tables, 'ny(h)', phi)
    # Now shape factors , 2x2 foundation
    B = 2
    L = 2
    #shape corrections
    sc=1+Nq/Nc*B/L
    sq=1+B/L*math.tan(phi*math.pi/180)
    sy=1-0.4*B/L
    #depth corrections
    dc = 1 +0.4*B/L
    dq = 1 +2*math.tan(phi*math.pi/180)*((1-math.sin(phi*math.pi/180))**2)*calc_depth/B
    dy=1
    q = calc_depth * gamma
    c_term = Cu*Nc*sc*dc
    q_term = q*Nq*sq*dq
    y_term = 0.5 * gamma * B * Ny*sy*dy
    if is_cohesive:
        y_term= 0.
    p = c_term + q_term + y_term
    #print(c_term,q_term,y_term)
    #print(mat)
    return(p/3)

def vesic_method(phi, gamma, Cu, calc_depth):
    is_cohesive = phi<=0.1
    Nq = getTable(m_tables, 'nq', phi)
    Nc = getTable(m_tables, 'nc', phi)
    Ny = getTable(m_tables, 'ny(v)', phi)
    # Now shape factors , 2x2 foundation
    B = 2
    L = 2
    #shape corrections
    sc=1+Nq/Nc*B/L
    sq=1+B/L*math.tan(phi*math.pi/180)
    sy=1-0.4*B/L
    #depth corrections
    dc = 1 +0.4*B/L
    dq = 1 +2*math.tan(phi*math.pi/180)*((1-math.sin(phi*math.pi/180))**2)*calc_depth/B
    dy=1
    q = calc_depth * gamma
    c_term = Cu*Nc*sc*dc
    q_term = q*Nq*sq*dq
    y_term = 0.5 * gamma * B * Ny*sy*dy
    if is_cohesive:
        y_term= 0.
    p = c_term + q_term + y_term
    #print(c_term,q_term,y_term)
    #print(mat)
    return(p/3)

def n_teng_method(N, calc_depth):
    B=2
    return 0.11*N*N*B+0.33*(100+N*N)*calc_depth

def get_bearing_capacity(input_datas, calc_depth):
    mat = get_top_material(input_datas, calc_depth)
    phi = mat[2]
    gamma = mat[5]
    Cu = mat[4]
    N60 = mat[7]
    terzaghi = terzagi_method(phi, gamma, Cu, calc_depth)
    meyerhof = meyerhof_method(phi, gamma, Cu, calc_depth)
    hansen = hansen_method(phi, gamma, Cu, calc_depth)
    vesic = vesic_method(phi, gamma, Cu, calc_depth)
    n_teng = n_teng_method(N60, calc_depth)
    return([terzaghi, meyerhof, hansen, vesic, n_teng])

def update_datas(input_datas):
    odbc_head = "Driver={Driver do Microsoft Access (*.mdb)}"
    db_path = os.getcwd()+"\\helper\\BHLog.DTA\\soildata.mdb"
    conn = pyodbc.connect("{};DBQ={};".format(odbc_head,db_path))
    cursor = conn.cursor()
    cursor.execute('select * from SoilNames where MatTypeName=?;', "Mohr-Coulomb")
    head = cursor.description
    row = cursor.fetchone()
    #Let's create inverse map for opposite operation
    map_pp = {}
    for i,data in enumerate(head):
        if row[i] and data[0]:
            if data[0].find('Name')!=-1:
                map_pp[row[i]]=''.join(data[0].split('Name'))
    template = 'UPDATE SoilData\n'
    template += ' SET'
    template += ' {} = ?,'.format(map_pp['G_ref'])
    template += ' {} = ?,'.format(map_pp['sin(phi)'])
    template += ' {} = ?,'.format(map_pp['c_ref'])
    template += ' {} = ?,'.format(map_pp['w_dry'])
    template += ' {} = ?,'.format(map_pp['w_wet'])
    template += ' {} = ?'.format(map_pp['nu'])
    template += ' \nWHERE ModelDesc = ?;'
    #print(template)
    # Req prop min
    for i in range(24):
        mat=get_top_material(input_datas, (i+1)/2)
        lname = str(i)
        phi = mat[2]
        c = mat[4]
        gamma = mat[5]
        nu = mat[6]
        E = mat[3]
        G = E / (1+nu) /2
        #update items
        params = (
            G,
            phi,
            c,
            gamma,
            gamma,
            nu,
            str(i+1)
        )
        cursor.execute(template, params)
    cursor.commit()
    conn.close()

def findWindow(win_class):
        return win32gui.FindWindow(win_class, None)

def update_data_cache():
    input_program = "C:\\Program Files (x86)\\Plaxis8x\\Geo.exe"
    file = os.getcwd()+"\\helper\\BHLog.plx"
    p=subprocess.Popen([input_program, file])
    time.sleep(0.5)
    window_class_main = 'TGeoMainForm'
    window_class_splash='TGeoSplash'
    while findWindow(window_class_splash):
        time.sleep(0.5)
    hwndMain = findWindow(window_class_main)
    time.sleep(0.5)
    win32gui.PostMessage(hwndMain, win32con.WM_COMMAND, 5, 0)
    ##########win32gui.PostMessage(hwndMain, win32con.WM_COMMAND, 19, 0)
    time.sleep(1)
    oldpos = pyautogui.position()
    pyautogui.click(518, 278)
    pyautogui.click(841, 380)
    pyautogui.moveTo(*oldpos)
    time.sleep(0.5)
    oldpos = pyautogui.position()
    pyautogui.click(744, 380)
    pyautogui.moveTo(*oldpos)

    #for auto clicker
    time.sleep(1)
    win32gui.PostMessage(hwndMain, win32con.WM_COMMAND, 19, 0)
    p.wait()

def plasix_method(input_datas):
    pass
    batch_program = "C:\\Program Files (x86)\\Plaxis8x\\batch.exe"
    # Now make file ready
    try:
        shutil.copy(os.getcwd()+"\\helper\\backup\\BHLog.plx",os.getcwd()+"\\helper\\")
    except:
        print('Cannot create file')
        pass
    try:
        shutil.copytree(os.getcwd()+"\\helper\\backup\\BHLog.DTA",os.getcwd()+"\\helper\\BHLog.DTA")
    except:
        print('Cannot create folder')
        pass
    file = os.getcwd()+"\\helper\\BHLog.plx"
    #Remove old force datas
    force_data_file = "C:\\Program Files (x86)\\Plaxis8x\\force.txt"
    try:
        os.unlink(force_data_file)
    except:
        pass
    update_datas(input_datas)
    update_data_cache()
    file="C:\\Program Files (x86)\\Plaxis8x\\Examples\\BHLog.plx"
    p=subprocess.Popen([batch_program, file])
    time.sleep(0.5)
    window_class_main = 'TBatchFrm'
    window_class_splash = 'TCalcSplash'
    window_class_calculation = 'TCalcForm'
    while findWindow(window_class_splash):
        time.sleep(0.5)
    # get main window hwnd, print(hwndMain)
    #calculate
    time.sleep(1.5)#more data more time to load,1.5:ok
    hwndMain = findWindow(window_class_main)
    win32gui.PostMessage(hwndMain, win32con.WM_COMMAND, 23, 0)
    # Wait for calculation to complete
    inertia = 3# 3 runs
    while True:
        wnd = findWindow(window_class_calculation)
        if wnd == 0:
            if inertia:
                inertia -= 1
            else:
                break
        time.sleep(0.75)# let's save some times this miss
    #save and exit
    win32gui.PostMessage(hwndMain, win32con.WM_COMMAND, 3, 0)
    win32gui.PostMessage(hwndMain, win32con.WM_COMMAND, 11, 0)
    p.wait()
    try:
        # now delete those files
        shutil.rmtree(os.getcwd()+"\\helper\\BHLog.DTA")
        os.unlink(os.getcwd()+"\\helper\\BHLog.plx")
    except:
        pass
    datas = []
    with open(force_data_file) as f:
        dat = f.read().splitlines()
        for i in dat:
            datas.append(float(i.split(' ')[1])*-2*math.pi/3)
    return(datas[1:])
    
def process_file(files):
    input_datas = files
    filtered = []
    for i in input_datas:
        filtered.append((float(i[0]),i[1],float(i[2]),float(i[3]),float(i[4]),float(i[5]),float(i[6]),float(i[7])))
    input_datas=filtered
    results = []
    for i in calc_depths:
        results.append(get_bearing_capacity(input_datas,i))
    plasix = plasix_method(input_datas)
    for i in range(len(results)):
        results[i].append(plasix[i])
    return results
    
def calculation(mat_file):
    results = []
    for i in mat_file:
        results.append(process_file(i))
    return results
#    helper.write_csv(file+'.afc', results)

#files = helper.getMyFiles('mtl', '.')
#files=files
#for i in files:
#    print()
#    print('Loading file:', i[0])
#    helper.give_file_hint(i[0])
#    try:
#        process_file(i)
#    except helper.helper_exception:
#        pass
#helper.print_failed()