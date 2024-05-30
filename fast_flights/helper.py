import numpy as np
import datetime
import pickle


PROCESS_STR="Learn more"
LOWERCASE_STR="abcdefghijklmnopqrstuvwxyz"
UPPERCASE_STR = LOWERCASE_STR.upper()
EXCEPT_LIST = ["easy, Jet", "Jet, Blue", "West, Jet"]
replace_dict = {"easy, Jet":"easyJet", "Jet, Blue":"JetBlue", "West, Jet":"WestJet"}
dict_cats = ["departure day","departure month","departure year","origin","destination","name","days","price","today",\
             "days ahead","flight duration","flight depart","flight arrive","stops","stops info"]

def modifyCaseChange(string):
    for i in range(1,len(string)):
        if string[i] in UPPERCASE_STR and string[i-1] in LOWERCASE_STR:
            return [string[:i],string[i:]]
    return [string]
    

def process_name(name):
    if PROCESS_STR in name:
        name =  name.split(PROCESS_STR)[1]
    #split airline names with commas
    if ',' in name:
        name = name.split(',')
    else:
        name = [name]
    final_str=[]
    for string in name:
        new_string_list = modifyCaseChange(string)
        for elem in new_string_list:
            final_str.append(elem)
    name = ', '.join(final_str)
    for i in EXCEPT_LIST:
        if i in name:
            name = name.replace(i,replace_dict[i])
    return name

def append_itin_to_dict(new_dict, fl, departure_day, departure_month, departure_year,\
                       origin, destination, days_ahead):
    new_dict["departure day"].append(departure_day)
    new_dict["departure month"].append(departure_month)
    new_dict["departure year"].append(departure_year)
    new_dict["origin"].append(origin)
    new_dict["destination"].append(destination)
    new_dict["name"].append(fl.name)
    new_dict["days"].append('')
    new_dict["price"].append(fl.price)
    new_dict["today"].append(datetime.datetime.today().strftime('%Y-%m-%d'))
    new_dict["days ahead"].append(days_ahead)
    new_dict["flight duration"].append(fl.duration)
    new_dict["flight depart"].append(fl.departure)
    new_dict["flight arrive"].append(fl.arrival)
    new_dict["stops"].append(fl.stops)
    new_dict["stops info"].append(fl.stops_text)
    return new_dict

def save_prog(itin_dict, name):
    with open(name, 'wb') as handle:
        pickle.dump(itin_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)  
    print("file updated")

#for domestic, search all one-way and two-way itineraries
def gen_itineraries(domestic_city_pairs, itin_type, num_days):
    itin_list=[]
    if itin_type=="domestic":
        base = datetime.datetime.today()
        date_list = [base + datetime.timedelta(days=x) for x in range(1,num_days)]
        date_list = [date.strftime('%Y-%m-%d') for date in date_list]
        for i in domestic_city_pairs:
            itin_name = '_'.join(i)            
            itin_name_rev = '_'.join(i[::-1])
            for j in date_list:
                itin_list.append('_'.join([itin_name, j]))                
                itin_list.append('_'.join([itin_name_rev, j]))
    return itin_list

def initialize_dict(new_dict):
    for i in dict_cats:
        new_dict[i]=[]
    return new_dict

def gen_dict_from_itin(itin):
    dict1={}
    for i in itin:
        dict1[i]=0
    return dict1
    
    