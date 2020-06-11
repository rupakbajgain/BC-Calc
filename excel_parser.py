# imports
import xlrd, openpyxl
import random
import re
split_helper = re.compile('[(,) :]')
import helper
import shutil

class fakeCell:
    def __init__(self, ty, val):
        self.ctype = ty
        self.value = val
        
    def __repr__(self):
        return str(self.value)

class cols:
    pass

def load_file(filename):
    sheet_list = {}
    if(filename.endswith('.xlsx')):
        workbook = openpyxl.load_workbook(filename)
        for sheet in workbook.worksheets:
            if sheet.max_row == 1:
                break
            bounds_list = []
            for i in sheet.merged_cells.ranges:
                bounds_list.append(i.bounds)
            row_list = []
            for row in sheet.iter_rows():
                col_list = []
                for cell in row:
                    mcell = {}
                    if cell.data_type=='n':
                        if cell.value:
                            mcell = fakeCell(2, cell.value)
                        else:
                            mcell = fakeCell(0, None)
                    elif cell.data_type=='s':
                        mcell = fakeCell(1, cell.value)
                    elif cell.data_type=='b':
                        mcell = fakeCell(4, cell.value)
                    elif cell.data_type=='e':
                        mcell = fakeCell(5, cell.value)
                    else:
                        mcell = fakeCell(0, None)
                    col_list.append(mcell)
                row_list.append(col_list)
            filtered_merges = []
            for (a,b,c,d) in bounds_list:
                    filtered_merges.append((a-1,b-1,c-1,d-1))
            # above line has no meaning
            print(filtered_merges)
            sheet_list[sheet.title] = (row_list, filtered_merges)
    else:
        workbook = xlrd.open_workbook(filename, formatting_info = True)
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            ncols = sheet.ncols
            if nrows==0:
                break #empty sheet
            row_list = []
            for row in range(sheet.nrows):
                col_list = []
                for col in range(sheet.ncols):
                    col_list.append(sheet.cell(row, col))
                row_list.append(col_list)
            filtered_merges = []
            for (a,b,c,d) in sheet.merged_cells:
                    filtered_merges.append((c,a,d-1,b-1))
            sheet_list[sheet.name] = (row_list, filtered_merges)
    return sheet_list

def get_header_row_1(row_list):
    # Now lets get the filtered contents of cells
    #list of words to guess table header, small letters
    table_header_hints = ['scale', 'depth', 'thickness', 'sampling', 'type', 'classification', 'group', 'symbol', 'spt', 'value', 
                         'n', 'gm', 'cm', 'm', '%', 'layer']
    def check_header_hit(text):
        words = split_helper.split(text)
        for i in words:
            if i in table_header_hints:
                return 1
            else:
                return 0
    score_list = []
    for i in range(len(row_list)):
        score = 0
        for j in range(len(row_list[i])):
            if row_list[i][j].ctype==1:
                score += check_header_hit(row_list[i][j].value.lower())
        score_list.append(score)
    header_row = 0
    for i in range(len(row_list)):
        if score_list[i] > score_list[header_row]:
            header_row = i
    if score_list[header_row] < 3: #SPT, depth, GI
        print('- Table not found')
        return None
    # for multi line header
    header_min = header_row
    header_max = header_row
    jump = True
    while(header_min>=0):
        if (score_list[header_min-1]>=score_list[header_row]/2):
            header_min -= 1
            jump = True
        elif jump:
            header_min -= 1
            jump = False
        else:
            break
    header_min += 1
    jump = True
    while(header_max<=len(row_list)):
        if (score_list[header_max+1]>=score_list[header_row]/2):
            header_max += 1
            jump = True
        elif jump:
            header_max += 1
            jump = False
        else:
            break
    header_max -= 1
    return (header_min, header_max)

def get_header_row_exp(header_min, header_max, merged):
    # Extend it even further on basis of merge_cell information if available
    for i in merged:
        #amin = amin-1
        (_, amin, _, amax)=i
        #print(header_min, header_max, '-' ,amin, amax, i)
        if (amin <= header_min and amax >= header_min):
            header_min = amin
        if (amin <= header_max and amax >= header_max):
            header_max = amax
    return (header_min, header_max)

def get_header_row(row_list, merged):
    header_row=get_header_row_1(row_list)
    if not header_row:
        print('Not a borehole log.')
        return None
    header_row=get_header_row_exp(header_row[0], header_row[1], merged)
    return header_row

def get_location(header, row_list):
    # Get location from headers
    expecting = False
    location = None
    for i in range(header[0]):
        for j in range(len(row_list[i])):
            c_val = row_list[i][j].value
            if c_val:
                if c_val.lower().find("location")!=-1:
                    expecting = True
                    if c_val.find(':')==-1:
                        continue
                if expecting:
                    guess = c_val.strip()
                    if len(guess)<3:
                        continue
                    is_loc = c_val.find(':')
                    if is_loc != -1:
                        guess = c_val[is_loc+1:].strip()
                    if guess!='':
                        location = guess
                        break
        if location:
            break
    if not location:
        helper.fail('Location not found')
    return location

def row_list_expand(row_list,merged):
    # Now lets copy values merged cells to every where
    def find_data(clo, rlo, chi, rhi):
        for i in range(rlo, rhi+1):
            for j in range(clo, chi+1):
                if row_list[i][j].value:
                    return row_list[i][j].value
    for i in merged:
        (clo, rlo, chi, rhi) = i
        for i in range(rlo, rhi+1):
            for j in range(clo, chi+1):
                row_list[i][j].ctype = 1
                row_list[i][j].value = find_data(clo, rlo, chi, rhi)
    return row_list

def get_map_var_row(row_list, header):
    # let's get max row size
    max_row_size = 0
    for i in range(header[0], header[1]+1):
        row_size = len(row_list[i])
        if max_row_size < row_size:
            max_row_size = row_size
    #
    map_var_row = []
    for j in range(max_row_size):
        map_var_row.append([''])
    for i in range(header[1], header[0]-1, -1):
        for j in range(max_row_size):
            cval = row_list[i][j].value
            if cval:
                last_index = len(map_var_row[j])-1
                if map_var_row[j][last_index].endswith(cval):
                    pass
                else:
                    if len(map_var_row[j][last_index]):
                        map_var_row[j][last_index]=row_list[i][j].value+' '+map_var_row[j][last_index]
                    else:
                        map_var_row[j][last_index]=row_list[i][j].value
    return map_var_row

def getBestColumn(map_var_row,rfields,forcedFields=[]):
    winners = []
    win_row = 0
    win_count = 0
    win_length = 0 #check only if more than one match(%)
    # Get the best field columnns for requested variables with hints
    for i,d in enumerate(map_var_row):
        this_row_count = 0
        this_word = ''
        for j in d:
            for k in rfields:
                this_word += j.lower()+' '
                if k in split_helper.split(j.lower()):
                    this_row_count += 1
        split_words = split_helper.split(this_word)
        this_length = len(split_words)
        found = True
        for k in forcedFields:
            if not k in split_words:
                found = False
                break
        if found:
            if this_row_count>win_count:
                win_row = i
                win_count = this_row_count
                winners = [i]
                win_length = this_length
            elif this_row_count==win_count:
                if win_length==this_length:
                    winners.append(i)
                elif win_length>this_length:
                    winners = [i]
    return winners

def getBestCols(map_var_row):
    columns = cols
    columns.spt_col = getBestColumn(map_var_row,['spt','n','value'])
    columns.depth_col = getBestColumn(map_var_row,['depth','m'], ['depth'])
    columns.sdepth_col = getBestColumn(map_var_row,['sampling', 'depth','m'], ['sampling', 'depth'])
    if len(columns.sdepth_col)<1:
        columns.sdepth_col = getBestColumn(map_var_row,['sampiling', 'depth','m'], ['sampiling', 'depth'])# spelling mistake
    columns.thickness_col = getBestColumn(map_var_row,['thickness','m'], ['thickness'])
    columns.classification = getBestColumn(map_var_row,['classification','soil'], ['classification'])
    columns.gsym = getBestColumn(map_var_row,['group','symbol'],['group'])
    columns.layer = getBestColumn(map_var_row,['layer'])
    columns.gamma = getBestColumn(map_var_row,['g','gm/cm3'])
    columns.wp = getBestColumn(map_var_row,['w','%'])
    return columns

#since we are not always sure
def get_all_data(row_list, header, col, ctype):
    # which column and valid data type
    out = []
    for i in range(header[1]+1, len(row_list)):
        try:
            cval = row_list[i][col]
            #print(cval.ctype)
            if cval.value:
                if cval.ctype==ctype:
                    out.append( (cval.value, i) )# and row too
        except:
            pass
    return out

def get_spt_data(row_list, spt_col, header):
    # For spt
    spt_data = []
    if len(spt_col)==1:
        spt_data = get_all_data(row_list, header, spt_col[0], 2)
    elif len(spt_col)==3:
        spt_data_0 = get_all_data(row_list, header, spt_col[0], 2)
        spt_data_1 = get_all_data(row_list, header, spt_col[1], 2)
        spt_data_2 = get_all_data(row_list, header, spt_col[2], 2)
        #calculating avg
        for i in range(len(spt_data_0)):
            spt_data.append((spt_data_0[i]+spt_data_1[i]+spt_data_2[i])/3)
    # lets assume our SPT is always less than 60
    spt_filtered = []
    for (n, row) in spt_data:
        if n<60.:
            spt_filtered.append((n, row))
    spt_data = spt_filtered
    if(len(spt_data)==0):
        helper.fail("No spt data found")
    spt_data.append((0., header[1]+1))
    return spt_data

def get_depth_data(row_list, depth_col, header, sdepth_col):
    # For depth
    depth_data = []
    if len(depth_col)==1:
        depth_data = get_all_data(row_list, header, depth_col[0], 2)
    #Use sampling depth datas too if available
    if len(sdepth_col)==1:
        depth_data.extend(get_all_data(row_list, header, sdepth_col[0], 2))
    #add first data too
    #use it if nothing is available
    # lets assume our depth is always less than 60
    depth_filtered = []
    for (n, row) in depth_data:
        if n<60.:
            depth_filtered.append((n, row))
    depth_data = depth_filtered
    if(len(depth_data)==0):
        helper.fail("No depth data found")
    depth_data.append((0., header[1]+1))
    return depth_data

def get_map_ds(spt_data, depth_data):
    # now create interpolated depth vs SPT
    map_d_s = []
    for (a, drow) in depth_data:
        amin = 0
        min_v = 0
        amax = 100
        max_v = 100
        found=False
        for (b, srow) in spt_data:
            if srow==drow:
                found=True
                map_d_s.append((a, b))
                break
            elif srow>amin and srow<drow:
                amin = srow
                min_v = b
            elif srow<amax and srow>drow:
                amax = srow
                max_v = b
        if not found:
            b = (max_v - min_v)/(amax - amin) * (drow- amin)  + min_v
            map_d_s.append((a, b))
    depth_update = []
    for (b, srow) in spt_data:
        amin = 0
        min_v = 0
        amax = 100
        max_v = 100
        found=False
        for (a, drow) in depth_data:
            if srow==drow:
                found=True
                break
            elif drow>amin and drow<srow:
                amin = drow
                min_v = a
            elif drow<amax and drow>srow:
                amax = drow
                max_v = a                
        if not found:
            a = (max_v - min_v)/(amax - amin) * (srow- amin)  + min_v
            map_d_s.append((a, b))
            depth_update.append((a, srow))
    depth_data.extend(depth_update)
    return(depth_data,map_d_s)

def get_gamma_data(row_list, gamma, header, wp):
    # For gamma
    gamma_data = []
    if len(gamma)==1:
        gamma_data = get_all_data(row_list, header, gamma[0], 2)
    #merge y with wp now if available
    gamma_filtered = []
    if len(wp)==1:
        for v, rv in gamma_data:
            if row_list[rv][wp[0]].ctype==2:
                w = row_list[rv][wp[0]].value
                if w:
                    gamma_filtered.append((v/(1+w/100)+1, rv))
                else:
                    gamma_filtered.append((v, rv))
        gamma_data = gamma_filtered            
    # lets assume our depth is always >1 and <4
    gamma_filtered = []
    for (n, row) in gamma_data:
        if n<4 and n>1:
            gamma_filtered.append((n*9.81, row))
    gamma_data = gamma_filtered
    return gamma_data
        
def get_map_d_g(depth_data, gamma_data):
    # Lets combine depth and gammas
    map_d_g = []
    for (a, drow) in depth_data:
        last_gamma = 0
        for (b, grow) in gamma_data:
            if grow <= drow:
                last_gamma = b
        map_d_g.append((a, last_gamma))        
    return map_d_g

def get_group_data(row_list, gsym, header, layer, classification):
    # Now let's search for soil group
    # Read group table automatically
    # First gain as much information about it
    letters = ['G','S','M','C','O', 'W','P','M','C','L','H', 'I', 'F','T']
    group_data = []
    if len(gsym)==1:
        group_data = get_all_data(row_list, header, gsym[0], 1)
    # now get all information from layer and classification
    helper_data = []
    if len(layer)==1:
        helper_data.extend(get_all_data(row_list, header, layer[0], 1))
    if len(classification)==1:
        helper_data.extend(get_all_data(row_list, header, classification[0], 1))
    #Now try to extract info from helper_data
    for (text, no) in helper_data:
        for i in split_helper.split(text):
            i = i.strip()
            if len(i)==1 or len(i)==2:
                group_data.append((i, no))
    ## Filter those datas
    group_filtered = []
    for (i, ro) in group_data:
        i = i.upper().strip()
        if len(i)==1:
            i=i+i
        if i[1]=="I": #Why I is it L
            i=i[0]+"L"
        if (i[1] in letters):
            group_filtered.append((i, ro))
    group_data = group_filtered
    if(len(group_data)==0):
        helper.fail("No group data found")
    return group_data

def get_map_d_sy(depth_data, group_data):
    # Lets combine depth and group symbol
    map_d_sy = []
    for (a, drow) in depth_data:
        for (b, grow) in group_data:
            if grow==drow:
                map_d_sy.append((a, b))        
    return map_d_sy

def analyse_sheet(sheet):
    row_list, merged = sheet
    header = get_header_row(row_list, merged)
    if not header:
        return None
    location = get_location(header, row_list)
    row_list = row_list_expand(row_list,merged)
    map_var_row = get_map_var_row(row_list, header)
    cols = getBestCols(map_var_row)
    spt_data = get_spt_data(row_list, cols.spt_col, header)
    depth_data = get_depth_data(row_list, cols.depth_col, header, cols.sdepth_col)
    #print(spt_data, depth_data, cols.sdepth_col)
    depth_data, map_d_s = get_map_ds(spt_data, depth_data)
    gamma_data = get_gamma_data(row_list, cols.gamma, header, cols.wp)
    map_d_g = get_map_d_g(depth_data, gamma_data)
    group_data = get_group_data(row_list, cols.gsym, header, cols.layer, cols.classification)
    map_d_sy = get_map_d_sy(depth_data, group_data)
    # combine and print
    all_depths = []
    for i,_ in depth_data:
        if not i in all_depths:
            all_depths.append(i)
    all_depths.remove(0.0)
    all_depths.sort()
    def find_data(depth,data):
        for (i,j) in data:
            if i==depth:
                return j
    res = []
    display=False
    sy_count = 0
    for i in all_depths:
        sy_data = find_data(i, map_d_sy)
        if sy_data:
            sy_count += 1
            res.append((i, sy_data, find_data(i, map_d_s), find_data(i, map_d_g)))
            if display:
                print(res[-1])
    if len(res)==0:
        helper.fail('No group data found')
    elif sy_count<4:
        helper.fail('Please merge the group data rows.')
    # Check log if we have enough information for 7.5m | 8m
    for i,_,_,_ in res:
        if i>=8:
            return (location, res)
    #else
    helper.fail('Depth data upto 7.5 not found')

def process_file(filename):
    sheets = load_file(filename)
    sheets_names = list(sheets.keys())
    #print('{} sheets found.'.format(len(sheets_names)))
    results=[]
    for name in sheets_names:
        helper.give_sheet_hint(name)
        #print('Parsing sheet:', name)
        result = analyse_sheet(sheets[name])
        if result:
            results.append((name, result))
    return results
    #for idx, i in enumerate(results):
    #    filtered = [(i[0],)]+i[1]
    #    if len(results)==1:
    #        helper.write_csv(file+'.ped',filtered)
    #    else:
    #        helper.write_csv(file+ '[' + sheets_names[idx] +']' +'.ped',filtered)
    #shutil.move('.\\unprocessed\\'+filename,'.\\processing\\')
    #for idx, i in enumerate(results):
    #    filtered = [(i[0],)]+i[1]
    #    if len(results)==1:
    #        helper.write_csv(file+'.ped',filtered)
    #    else:
    #        helper.write_csv(file+ '[' + sheets_names[idx] +']' +'.ped',filtered)
    #print(results)

#files = helper.getMyFiles('xls', '.', 'temp')
#files.extend(helper.getMyFiles('xlsx', '.', 'temp'))
#for i in files:
#    print('Loading file:', i[0])
#    helper.give_file_hint(i[0])
#    try:
#        process_file(i)
#    except helper.helper_exception:
#        pass
#helper.print_failed()


def excel_parser(file):
    helper.give_file_hint(file)
    return process_file(file)