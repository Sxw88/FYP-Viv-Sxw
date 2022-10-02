#!/usr/bin/env python3

import json
import socket

def writeJSON(field_name, field_ID, field_desc):
    """Write one (1) JSON data to file"""
    # JSON data to append
    JSON_data = {
        field_ID : {
            "Name": field_name,
            "Desc": field_desc
        }
    }

    JSON_list = readJSONList()
    JSON_list.append(JSON_data)
    
    with open('person.json', 'w') as output_file:
        json.dump(JSON_list, output_file, indent=2)


def readJSONList():
    """Reads entire JSON List From file"""
    with open('person.json', 'r') as read_file:
            obj_list = []
            obj_list = json.load(read_file)
            return obj_list


def readJSONData(obj_list, key, index):
    """Reads JSON Data from List"""
    obj_count = 0
    
    for n in obj_list:
        obj_count += 1
        if obj_count == index:
            return(n[key])

def setJSONValue(obj_list, index, key, new_value):
    """sets JSON value given key and index"""
    obj_count = 0

    for n in obj_list:
        obj_count += 1
        if obj_count == index:
            n[key] = new_value

    with open('person.json', 'w') as output_file:
        json.dump(obj_list, output_file, indent=2)


    
if __name__ == "__main__":
    #call the functions
    writeJSON("Joe", "1234", "Human from Earth")
    writeJSON("Mickey", "4321", "A Mouse")

    JSON_LIST = readJSONList()
    print(JSON_LIST)
    #print(readJSONData(JSON_LIST,"Name",2))
    #print(readJSONData(JSON_LIST,"ID",2))
    #print(readJSONData(JSON_LIST,"Description",2))

    #setJSONValue(JSON_LIST, 2,"ID", "8888")
    #print(readJSONData(JSON_LIST,"Name",2))
    #print(readJSONData(JSON_LIST,"ID",2))
    #print(readJSONData(JSON_LIST,"Description",2))


