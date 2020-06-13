# imports
import helper
import random
import math

#distribution radius for each location
locations_rad =[]
locations=[]

def distance(x,y):
    return (x[1]-y[1])**2+(x[2]-y[2])**2

def init_location_service():
    global locations
    filtered = []
    for i in locations:
        filtered.append((i[0], float(i[1]), float(i[2])))
    locations=filtered
    for i in locations:
        nearest=locations[0]
        dist=100000000000
        for j in locations:
            dists = distance(i,j)
            if dists>0.0001:
                if dists<dist:
                    dist=dists
        locations_rad.append(dist)
    #print(locations_rad)

# randomly distiributed location
def get_location(loc):
    loc = loc + ', Nepal'
    idxx = 0
    for idx,i in enumerate(locations):
        if i[0].lower().strip()==loc.lower().strip():
            idxx=idx
            break
    rangle = random.uniform(0,2*math.pi)
    rdist = random.uniform(0,locations_rad[idxx])
    lat = locations[idxx][1] + rdist * math.sin(rangle)
    long = locations[idxx][2] + rdist * math.cos(rangle)
    return (lat, long)

results = []
def process_file(files):
    filename, file = files
    input_datas = helper.load_csv(filename,'.\\datas\\result\\')
    loc = input_datas[0][1]
    lat,long = get_location(loc)
    for i in range(1,4):
        results.append((file,loc,input_datas[1][i],input_datas[2][i],input_datas[3][i],input_datas[4][i],input_datas[5][i],input_datas[6][i],input_datas[7][i],lat,long))
    results.append(())
    filtered = []

results.append(['file','location','depth','terzaghi','meyerhof','hansen','vesic','teng','plasix','lat','long'])
if __name__=='__main__':
    files = helper.getMyFiles('csv', '.', '.\\datas\\result\\')
    locations = helper.load_csv('locations.csv','.\\datas\\helper\\')
    init_location_service()
    for i in files:
        print()
        print('Loading file:', i[0])
        helper.give_file_hint(i[0])
        try:
            process_file(i)
        except helper.helper_exception:
            pass
    helper.print_failed()
    helper.write_csv('result.csv',results,'.\\datas\\')