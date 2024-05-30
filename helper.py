import numpy as np
import datetime
import pickle
import random
from fast_flights import FlightData, Passengers, create_filter, get_flights, Bags
import pandas as pd
import os.path
import time

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
                       origin, destination, days_ahead, days):
    new_dict["departure day"].append(departure_day)
    new_dict["departure month"].append(departure_month)
    new_dict["departure year"].append(departure_year)
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
    return new_dict

def save_prog(itin_dict, name):
    with open(name, 'wb') as handle:
        pickle.dump(itin_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)  
    print("file updated")

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
    for key in itin_dict:
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
        departure_day, departure_month, departure_year = departure_date.split('-')
        days_ahead = (datetime.datetime.strptime(departure_date, "%Y-%m-%d") - datetime.datetime.today()).days
        new_dict={}
        new_dict=initialize_dict(new_dict)
        # Create a new filter
        cookies = { "CONSENT": "YES+" }
        filter = create_flight_filter(key, mode, origin, destination, departure_date, return_date)
        result = get_flights_wrapper(filter, cookies)
        if result == []:
#             print("Will retry, exception occured")
            num_unfinished+=1
            continue
        if len(result.flights)==0:
#             print("0 flights returned. Will retry")
            num_unfinished+=1
            continue    
        for i in range(len(result.flights)):
            fl = result.flights[i]
    #         print(fl.price)
            new_dict = append_itin_to_dict(new_dict, fl, departure_day, departure_month, departure_year,\
                                                 origin, destination, days_ahead,days)
#         print(len(result.flights)," flights found")
        itin_dict[key] = new_dict
    #     createDfAndPrint(new_dict)
        save_prog_count+=1
        end = time.time()
#         print(key," completed")
#         print("time_elapsed: ",end-start)
    save_prog(itin_dict, folder_path+date_today_file)
    return num_unfinished

    