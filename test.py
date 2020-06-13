import time
import sys
import shutil,os
from excel_parser import excel_parser
from material_creater import material_creater
from calculation import calculation
import helper

methods = ['terzaghi','meyerhof','hansen','vesic','teng','plasix']
def process_file(name, display=False):
    e_res = excel_parser(name)
    mat = material_creater(e_res)
    calc = calculation(mat)
    results=[]
    for i in range(len(e_res)):
        result = []
        result.append(e_res[i][0])
        result.append(e_res[i][1][0])
        if display:
            print('\nSheet:', e_res[i][0])
            print('Location:', e_res[i][1][0])
        cdata = calc[i]
        result.append(cdata)
        if display:
            for idx,j in enumerate(cdata):
                print('Depth : ', 1.5*(idx+1))
                for idx2,j in enumerate(j):
                    print(methods[idx2],':', j)
        results.append(result)
    return results

#to be called by other programs
def get_result_from_file_data(data, filename):
    tmpdir = os.getcwd()+'\\temp\\'
    try:
        shutil.rmtree(tmpdir)
    except:
        pass
    os.mkdir(tmpdir)
    #create file
    with open(tmpdir+filename, 'wb') as f:
        f.write(data)
    try:
        result = process_file(tmpdir+filename)
    except:
        return helper.fail_string()
    return result

#Solve single file
if __name__=='__main__':
    if len(sys.argv)!=2:
        print('Filename required as first parameter.')
    else:
        tmpdir = os.getcwd()+'\\temp\\'
        file=sys.argv[1]
        dpos = file.rfind('\\')
        filename = file[dpos+1:]
        try:
            shutil.rmtree(tmpdir)
        except:
            pass
        os.mkdir(tmpdir)
        shutil.copy(file, tmpdir)
        try:
            process_file(tmpdir+filename, display=True)
        except helper.helper_exception:
            helper.print_failed()
    os.system('pause')