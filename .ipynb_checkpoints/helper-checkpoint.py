import numpy as np
import datetime
import pickle
import random
from fast_flights import FlightData, Passengers, create_filter, get_flights, Bags
import pandas as pd
import os.path
import time
from ipywidgets import IntProgress
from IPython.display import display
from tqdm.notebook import tqdm
from os import listdir
from os.path import isfile, join
import sqlite3

PROCESS_STR="Learn more"
LOWERCASE_STR="abcdefghijklmnopqrstuvwxyz"
UPPERCASE_STR = LOWERCASE_STR.upper()
EXCEPT_LIST = ["easy, Jet", "Jet, Blue", "West, Jet"]
replace_dict = {"easy, Jet":"easyJet", "Jet, Blue":"JetBlue", "West, Jet":"WestJet"}
dict_cats = ["origin","destination","name","days","price","today",\
             "days ahead","flight duration","flight depart","flight arrive","stops","stops info","departure date"]
sql_cats = ["origin","destination","name","days","price","today",\
             "days_ahead","flight_duration","flight_depart","flight_arrive","stops","stops_info","departure_date"]

def createInitialDBTable(cursor):
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS data_table (
        id INTEGER PRIMARY KEY,
        origin TEXT,
        destination TEXT,
        name TEXT,
        days INTEGER,
        price TEXT,
        today TEXT,
        days_ahead INTEGER,
        flight_duration TEXT,
        flight_depart TEXT,
        flight_arrive TEXT,
        stops TEXT,
        stops_info TEXT,
        departure_date TEXT
    )
    '''    
    cursor.execute(create_table_query)
    return cursor
    

def addDictToDB(itin_dict, cursor):
    #assumes that the DB is already created
    for outer_key, inner_dict in itin_dict.items():
        if isEmpty(inner_dict):
            continue
        num_rows = len(inner_dict["origin"])
        for i in range(num_rows):  
            row = []
            for inner_key, values in inner_dict.items():
                row.append(values[i])
            # Insert the row into the table (excluding the id column)
            insert_query = f"INSERT INTO data_table ({', '.join(sql_cats)}) VALUES ({', '.join(['?']*len(dict_cats))})"
            cursor.execute(insert_query, row)
    return cursor

def returnDBFromFile(DB_filename, mode, folder_location):
    conn = sqlite3.connect(folder_location+DB_filename+'_'+mode+'.db')
    cursor = conn.cursor()
    return conn, cursor

def closeDB(conn, cursor):
    conn.commit()
    conn.close()    

def addDictToDBFromFile(DB_filename, mode, folder_location, itin_dict):
    conn, cursor = returnDBFromFile(DB_filename, mode, folder_location)
    cursor = addDictToDB(itin_dict, cursor)
    closeDB(conn, cursor)

def createDBFromDictFiles(DB_filename, mode, folder_location):
    conn, cursor = returnDBFromFile(DB_filename, mode, folder_location)
    cursor = createInitialDBTable(cursor)
    files = [f for f in listdir(folder_location) if isfile(join(folder_location, f))]
    if mode=='intl':
        files = [f for f in files if mode in f and '.pkl' in f]
    else:
        files = [f for f in files if 'intl' not in f and '.pkl' in f]
    progress_bar = tqdm(total=len(files), desc='Processing Files')
    i=1
    for f in files:
        progress_bar.n = i
        progress_bar.refresh()
        with open(folder_location+f, 'rb') as handle:
            itin_dict = pickle.load(handle) 
            cursor = addDictToDB(itin_dict, cursor)
        i+=1
    # Commit the changes and close the connection
    closeDB(conn, cursor)
    

def getAllFlightData(origin, destination, folder_location, exclusion_list):
    files = [f for f in listdir(folder_location) if isfile(join(folder_location, f))]
    files = [f for f in files if f not in exclusion_list]
    aggregateDf = pd.DataFrame()
    city_prefix1 = '_'.join([origin, destination])
    city_prefix2 = '_'.join([destination, origin])
    for f in files:
        with open(folder_location+f, 'rb') as handle:
            itin_dict = pickle.load(handle) 
            for key in init_dict:
                if city_prefix1 not in key and city_prefix2 not in key:
                    continue
                data = pd.DataFrame(itin_dict[key])
                if aggregateDf.empty:
                    aggregateDf = data
                else:
                    aggregateDf = pd.concat([aggregateDf, data], axis=0, ignore_index=True)
    return aggregateDf

def isEmpty(new_dict):
    if new_dict==0:
        return True
    return False
    
def repairPkl(folder_location, exclusion_list):
    files = [f for f in listdir(folder_location) if isfile(join(folder_location, f))]
    files = [f for f in files if f not in exclusion_list and '.pkl' in f]
    num_entries=0
    for f in files:
        print(f)
        with open(folder_location+f, 'rb') as handle:
            itin_dict = pickle.load(handle) 
            key_list = list(itin_dict.keys())
            for key in itin_dict:
                new_dict = itin_dict[key]
                if isEmpty(new_dict):
                    continue
                num_entries+=1
                dep_date = key.split('_')[2]
                dep_date_list = [dep_date]*len(new_dict["departure year"])
                new_dict["departure date"] = dep_date_list
                del new_dict["departure year"]
                del new_dict["departure month"]
                del new_dict["departure day"]
                itin_dict[key] = new_dict

        with open(folder_location+f, 'wb') as handle:
            pickle.dump(itin_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)  
        print(num_entries," entries repaired")
    

def getItinDfFromAggDf(origin, destination, aggDf, duration, mode):
    city_prefix1 = '_'.join([origin, destination])
    city_prefix2 = '_'.join([destination, origin])
    if mode=="domestic":
        one_way_df = aggDf[(aggDf["origin"]==origin)&(aggDf["destination"]==destination)]
        return_df = aggDf[(aggDf["origin"]==destination)&(aggDf["destination"]==origin)]
        for index, row in one_way_df.iterrows():
            dep_date = datetime.datetime.strptime(row["departure date"], "%Y-%m-%d")
            target_date = (dep_date + datetime.timedelta(days=duration)).strftime('%Y-%m-%d')
            return_flight = return_df[return_df["departure date"]==target_date]

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

def append_itin_to_dict(new_dict, fl, departure_date, origin, destination, days_ahead, days):
    new_dict["origin"].append(origin)
    new_dict["destination"].append(destination)
    new_dict["name"].append(fl.name)
    new_dict["days"].append(days)
    new_dict["price"].append(fl.price)
    new_dict["today"].append(datetime.datetime.today().strftime('%Y-%m-%d'))
    new_dict["days ahead"].append(days_ahead)
    new_dict["flight duration"].append(fl.duration)
    new_dict["flight depart"].append(fl.departure)
    new_dict["flight arrive"].append(fl.arrival)
    new_dict["stops"].append(fl.stops)
    new_dict["stops info"].append(fl.stops_text)
    new_dict["departure date"].append(departure_date)
    return new_dict

def save_prog(itin_dict, name):
    with open(name, 'wb') as handle:
        pickle.dump(itin_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)  
#     print("file updated")

#for domestic, search all one-way and two-way itineraries
def gen_itineraries(city_pairs, itin_type, num_days, num_itins=100):
    itin_list=[]
    base = datetime.datetime.today()
    if itin_type=="domestic":
        date_list = [base + datetime.timedelta(days=x) for x in range(1,num_days)]
        date_list = [date.strftime('%Y-%m-%d') for date in date_list]
        for i in city_pairs:
            itin_name = '_'.join(i)            
            itin_name_rev = '_'.join(i[::-1])
            for j in date_list:
                itin_list.append('_'.join([itin_name, j]))                
                itin_list.append('_'.join([itin_name_rev, j]))
    else:
        for i in city_pairs:
            origin, dest, duration_list = i
            city_pair = str(origin)+'_'+str(dest)+'_'
            city_itin_list=[]
            for duration in duration_list:
                days_list = random.sample(range(1, num_days), num_itins)
                date_list = [[base + datetime.timedelta(days=x), base + datetime.timedelta(days=x+duration)] for x in days_list]
                date_list = [[x[0].strftime('%Y-%m-%d'), x[1].strftime('%Y-%m-%d')] for x in date_list]
                date_list = ['_'.join(x) for x in date_list]
                date_list = [city_pair+x for x in date_list]
                city_itin_list.extend(date_list)
            itin_list.extend(city_itin_list)        
    return itin_list

def initialize_dict(new_dict):
    for i in dict_cats:
        new_dict[i]=[]
    return new_dict

def create_flight_filter(key, mode, origin, destination, departure_date, return_date):
    if mode=="domestic":
        filter = create_filter(
        flight_data=[
            # Include more if it's not a one-way trip
            FlightData(
                date=departure_date,  # Date of departure
                from_airport=origin, 
                to_airport=destination
            ),
            # ... include more for round trips and multi-city trips
        ],
        bags=Bags(
            carryon=1,
            checked=0
        ),
        trip="one-way",  # Trip (round-trip, one-way, multi-city)
        seat="economy",  # Seat (economy, premium-economy, business or first)
        passengers=Passengers(
            adults=1,
            children=0,
            infants_in_seat=0,
            infants_on_lap=0
        ),
        )
    else:
        filter = create_filter(
        flight_data=[
            # Include more if it's not a one-way trip
            FlightData(
                date=departure_date,  # Date of departure
                from_airport=origin, 
                to_airport=destination
            ),
            FlightData(
                date=return_date,  # Date of departure
                from_airport=destination, 
                to_airport=origin
            ),
            # ... include more for round trips and multi-city trips
        ],
        bags=Bags(
            carryon=1,
            checked=0
        ),
        trip="round-trip",  # Trip (round-trip, one-way, multi-city)
        seat="economy",  # Seat (economy, premium-economy, business or first)
        passengers=Passengers(
            adults=1,
            children=0,
            infants_in_seat=0,
            infants_on_lap=0
        ),
        )
    return filter

def get_flights_wrapper(filter, cookies):
    result = get_flights(filter, cookies=cookies)
    return result

def createDfAndPrint(data):
    aggregateDf = pd.DataFrame(data)
    with pd.option_context('display.max_colwidth', None,'display.max_rows', None):
        display(aggregateDf)    
        
def gen_dict_from_itin(itin):
    dict1={}
    for i in itin:
        dict1[i]=0
    return dict1
    
def update_dict(itin_dict, folder_path, date_today_file, mode):
    save_prog_count=0
    num_unfinished=0
    total_keys = len(itin_dict.keys())
#     f = IntProgress(min=0, max=100) # instantiate the bar
#     display(f)
    progress_bar = tqdm(total=total_keys, desc='Processing')
    key_num=0
    total_flights_found=1
    total_routes_searched = 1
    for key in itin_dict:
#         f.value = int((key_num*100)/total_keys)
        progress_bar.n = key_num
        progress_bar.refresh()
        progress_bar.set_postfix_str(f'{total_flights_found/total_routes_searched}/{total_routes_searched} avg flights')
        key_num+=1
        if itin_dict[key]!=0:
            continue
        if save_prog_count==10:
            save_prog_count = 0
            save_prog(itin_dict, folder_path+date_today_file)
        start = time.time()
        if mode=="domestic":
            origin, destination, departure_date = key.split('_')
            return_date=0
            days=''
        else:
            origin, destination, departure_date, return_date = key.split('_')
            days = (datetime.datetime.strptime(return_date, "%Y-%m-%d") - \
                    datetime.datetime.strptime(departure_date, "%Y-%m-%d")).days
        days_ahead = (datetime.datetime.strptime(departure_date, "%Y-%m-%d") - datetime.datetime.today()).days
        new_dict={}
        new_dict=initialize_dict(new_dict)
        # Create a new filter
        cookies = { "CONSENT": "YES+" }
        filter = create_flight_filter(key, mode, origin, destination, departure_date, return_date)
        result = get_flights_wrapper(filter, cookies)
        if result == []:
            num_unfinished+=1
            continue
        if len(result.flights)==0:
            num_unfinished+=1
            continue 
        total_flights_found+= len(result.flights) 
        total_routes_searched+=1
        for i in range(len(result.flights)):
            fl = result.flights[i]
            new_dict = append_itin_to_dict(new_dict, fl, departure_date,origin, destination, days_ahead,days)
        itin_dict[key] = new_dict
        save_prog_count+=1
        end = time.time()
    progress_bar.close()
    save_prog(itin_dict, folder_path+date_today_file)
    return num_unfinished

    