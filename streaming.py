"""
This file defines the functions that will be used to explore the Actyx API.
This script checks the list of machines after every 5 seconds to see if their currents are within their thresholds.
"""

import urllib2
import json
import time
from collections import defaultdict


"""
This function defines the function that takes as an argument the url to the API and returns a list of all the
machines with their ID's

input

machines_url : A simple url to the API machines

output

machines_list: A list of all the machines with their ID's
"""


def get_machine_list(machines_url):

    # getting the JSON response from the API. each entry of this response contains a url to the individual machines

    json_obj = urllib2.urlopen(machines_url)
    data = json.load(json_obj)

    # initializing the empty machines_list

    machines_list = []

    # splitting the url on '/' and getting the machine ID at the third index of the split url
    for entry in data:
        machines_list.append(str(entry).split('/')[2])

    return machines_list

"""
This function takes the url for an individual machine and returns its sensor data as JSON response

input

machine_url_list: The list of urls to all machines

output

machine_data_list: The JSON response of every machine's sensor data in a list
"""


def get_machine_data(machine_url_list):

    # initializing the empty machine_data_list
    machine_data_list = []

    # Getting the JSON response from the API for the machine. each entry of this response contains a sensor value

    # Repeating this process for all the machines
    for machine in machine_url_list:

        # Constructing the url
        machine_url = "http://machinepark.actyx.io/api/v1/machine/" + str(machine)

        # Retrieving the JSON response of the sensor data and appending it to the list

        json_obj = urllib2.urlopen(machine_url)
        data = json.load(json_obj)
        machine_data_list.append(data)

    return machine_data_list

"""
This function checks the current drawn by each machine after every 5 seconds and checks if it is within the threshold

input

machine_data_list: The list of JSON sensor data to all machines
"""


def check_current(machine_data_list):

    # Defining the average current interval as 5 minutes

    timeout = time.time() + 60*5   # 5 minutes from now

    # Defining the has map for current data of previous 5 minutes for each machine

    current_hash_map = defaultdict(list)

    while True:

        # Going through each of the machines

        for machine_data in machine_data_list:

            # Updating the moving window based on the 5 min interval. i.e. after 5 min del from the head and insert
            # at te tail whenever you see a new value

            if time.time() < timeout:
                current_hash_map[str(machine_data['name'])].append(float(machine_data['current']))
            else:
                del current_hash_map[str(machine_data['name'])][0]
                current_hash_map[str(machine_data['name'])].append(float(machine_data['current']))

            # Checking if the current drawn is above the threshold

            if float(machine_data['current']) > float(machine_data['current_alert']):
                average_current = float(sum(current_hash_map[str(machine_data['name'])]))/float(len(current_hash_map[str(machine_data['name'])]))
                print str(machine_data['name']) + " is drawing current: " + str(machine_data['current']) + " more than threshold: " + str(machine_data['current_alert']) + " average current drawn in past five min is: " + str(average_current)

        #  call the API for data after every 5 seconds

        time.sleep(5)


if __name__ == '__main__':
    url = "http://machinepark.actyx.io/api/v1/machines"
    machines = get_machine_list(url)
    machines_data = get_machine_data(machines)
    check_current(machines_data)

