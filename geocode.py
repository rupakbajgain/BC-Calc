import helper
from geopy.geocoders import Nominatim,AlgoliaPlaces,ArcGIS,GeocodeFarm
import time
import random

services = [Nominatim,AlgoliaPlaces,ArcGIS,GeocodeFarm]

results = []
onLine=True

def fetchGeo(name):
    random.shuffle(services)
    for i in services:
        try:
            locator = i(user_agent='myGeocoder')
            location = locator.geocode(name)
            return((location.latitude, location.longitude))
        except:
            pass
    return None

def findGeocode(oname):
    global results
    name = oname + ', Nepal'
    old_query  =False
    for i,l,lo in results:
        if i.lower().strip()==name.lower().strip():
            if l!="":
                return (l,lo)
            else:
                old_query=True
                break
    res = ['', '']
    if not old_query:
        #print('New')
        res = fetchGeo(name)
        if res:
            results.append([name, res[0], res[1]])
            flush()
        else:
            results.append([name, '', ''])
    else:
        if onLine:
            res = fetchGeo(name)
            if res:
                #print(res)
                results.remove([name, '', ''])
                results.append([name, res[0], res[1]])
                flush()
    if res==['','']:
        helper.fail_safe(oname)
    return res

def flush():
    helper.write_csv('locations.csv',results,'.\\datas\\helper\\')

def process_file(files):
    filename, file = files
    loc=helper.load_csv(filename,'.\\datas\\result\\')[0][1]
    f = findGeocode(loc)
    print(loc,f)

if __name__=='__main__':
    try:
        results.extend(helper.load_csv('locations.csv','.\\datas\\helper\\'))
    except:
        pass
    for i in files:
        print()
        print('Loading file:', i[0])
        helper.give_file_hint(i[0])
        try:
            process_file(i)
        except helper.helper_exception:
            pass
    helper.print_failed()
    flush()