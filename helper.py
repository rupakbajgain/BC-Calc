import os
import csv

# Get all files with that extension that have not been processed
def getMyFiles(in_ext, out_extension,searchLocation):
    out = []
    files = os.listdir('./'+searchLocation)
    #change all to small case
    for i in files:
        out.append(i.lower())
    files=out
    out = []
    #now select with given condition
    for i in files:
        dpos = i.rfind('.')
        filename,ext = (i[:dpos],i[dpos+1:])
        if in_ext!=ext:
            continue
        out_file_found=False
        for j in files:
            if i==j:
                continue
            dpos = j.rfind('.')
            filename2, ext2 = (j[:dpos],j[dpos+1:])
            if filename==filename2 and out_extension==ext2:
                out_file_found=True
                break
        if not out_file_found:
            out.append((i, filename))
    return out
    
failed_files = []
current_file = ''
current_sheet = ''
def give_file_hint(name):
    global current_file
    current_file = name

def give_sheet_hint(name):
    global current_sheet
    current_sheet = name

class helper_exception(Exception):
    def __init__(self, msg):
        self.msg = msg
    
    def get(self):
        return self.msg

def fail_safe(msg):
    failed_files.append((current_file, msg, current_sheet))

def fail(msg):
    #fail with throwing error
    failed_files.append((current_file, msg, current_sheet))
    raise helper_exception(msg)
 
def print_failed():
    print("--------------------------------- Failed Files --------------------------------")
    for i in failed_files:
        if i[2]:
            print(i[0],'[{}]:'.format(i[2]),i[1])
        else:
            print(i[0], ':' ,i[1])
    print("-------------------------------------------------------------------------------")
    
def fail_string():
    #for single usage only
    t=''
    for i in failed_files:
        t+='\n[{}]: '.format(i[2]) + i[1]
    return t

def write_csv(filename, data, dir_n):
    with open(dir_n+filename, 'w', newline="") as csv_file:
        writer = csv.writer(csv_file)
        for i in data:
            writer.writerow(i)
    
def load_csv(filename, dir_n):
    out = []
    with open(dir_n+filename) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            out.append(row)
    return out
