import numpy as np
PROCESS_STR="Learn more"
LOWERCASE_STR="abcdefghijklmnopqrstuvwxyz"
UPPERCASE_STR = LOWERCASE_STR.upper()
EXCEPT_LIST = ["easy, Jet", "Jet, Blue", "West, Jet"]
replace_dict = {"easy, Jet":"easyJet", "Jet, Blue":"JetBlue", "West, Jet":"WestJet"}

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
        