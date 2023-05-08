import nipyapi
from nipyapi import canvas,config
import urllib
import pandas as pd
import json
import base64
import datetime
import time
import configparser
import re



#TODO Write README.md
# Import Configurations from config.ini 
config = configparser.ConfigParser()
config.read('config.ini')
USERNAME = config.get('CONFIG', 'USERNAME')
PASSWORD = config.get('CONFIG', 'PASSWORD')
ENDPOINT = config.get('CONFIG', 'ENDPOINT')
OUTPUT_LOCATION = config.get('CONFIG', 'OUTPUT_LOCATION')


nipyapi.config.nifi_config.force_basic_auth = True

#Setup environement
nipyapi.utils.set_endpoint(ENDPOINT)
#Login to Nifi Service
nipyapi.security.service_login(service='nifi', username=USERNAME, password=PASSWORD)

root_id = canvas.get_root_pg_id()
all_connections = nipyapi.canvas.list_all_connections(root_id)


def get_pg_name(pg_id):
    """
    Each connection returns Process Group ID. This Function will use the PG ID to return Process Group Name
    """
    get_pg = nipyapi.canvas.get_flow(pg_id)
    return get_pg.process_group_flow.breadcrumb.breadcrumb.name

def queued_duration(connection_id):
    """
    Queries each Connection ID and fetches List URL. 

    List URL generates a list of 100 flow file objects in the list of which the one with the Max Queued Duration is taken

    Max Queued Duration time is converted to Days and returned by this function
    """
    listing_requests = nipyapi.nifi.apis.flowfile_queues_api.FlowfileQueuesApi().create_flow_file_listing(connection_id)
    request = urllib.request.Request(listing_requests.listing_request.uri)
    base64string = base64.b64encode(bytes('%s:%s' % (USERNAME, PASSWORD),'ascii'))
    request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
    with urllib.request.urlopen(request) as url:
        data = json.load(url)
    #TODO Add Exception for empty queue if needed
    queued_duration = max(data["listingRequest"]["flowFileSummaries"], key=lambda ev: ev["queuedDuration"])
    delta = datetime.timedelta(milliseconds=queued_duration["queuedDuration"])
    days = delta.days + delta.seconds / (24 * 60 * 60) + delta.microseconds / (24 * 60 * 60 * 1000000)
    return days

def get_name_values(d, names=[]):
    """
    Recursively extract name values from a nested dict.
    """
    if isinstance(d, dict):
        if 'name' in d:
            names.append(d['name'])
        for k, v in d.items():
            get_name_values(v, names)
    elif isinstance(d, list):
        for item in d:
            get_name_values(item, names)
    return names

def get_root_path(pg_id):
    """
    Generates root path using PG ID of the connection

    The get_name_values() recursively iterates one level up till it reaches the root ID

    The function returns a list of names of all the PGs starting from the connection up to the Root Path
    """
    get_pg = nipyapi.canvas.get_flow(pg_id)
    request = urllib.request.Request(get_pg.process_group_flow.uri)
    base64string = base64.b64encode(bytes('%s:%s' % (USERNAME, PASSWORD),'ascii'))
    request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
    with urllib.request.urlopen(request) as url:
        data = json.load(url)
    # use a loop to navigate to the 'name' values
    name = []
    breadcrumb = data['processGroupFlow']['breadcrumb']
    names = get_name_values(breadcrumb, name)
    return names
    


pg_id = []
connection_id = []
flow_count = []

#Populate above declared lists with values from all_connections 
for conns in range(0, len(all_connections)):
    #if int(re.sub("bytes", "", all_connections[conns].status.aggregate_snapshot.queued_size)) == 0: #Change queued_size to queued_count on HMS side
    if int(re.sub(",", "", all_connections[conns].status.aggregate_snapshot.queued_count)) >25000: #Change queued_count to queued_size on HMS side
        pg_id.append(all_connections[conns].source_group_id)
        connection_id.append(all_connections[conns].id)
        flow_count.append(all_connections[conns].status.aggregate_snapshot.queued_count)
    

#Dataframe setup

#final_path = []
start = time.time()
pg_id_series = pd.Series(pg_id)
connection_id_series = pd.Series(connection_id)
flow_count_series = pd.Series(flow_count)
clean_data = pd.DataFrame(columns = ['Process_Group_Name', 'Process_Group_ID', 'Connection_ID', 'Flow_File_Count','Max_Queued_Duration', 'Root_path'])
clean_data["Process_Group_ID"] = pg_id_series.values
clean_data["Connection_ID"] = connection_id_series.values
clean_data["Flow_File_Count"] = flow_count_series.values
clean_data["Max_Queued_Duration"] = clean_data['Connection_ID'].apply(queued_duration)
clean_data=clean_data[clean_data["Max_Queued_Duration"] > 1]
clean_data["Process_Group_Name"] = clean_data['Process_Group_ID'].apply(get_pg_name)
clean_data["Root_path"] = clean_data['Process_Group_ID'].apply(get_root_path)
end = time.time()
print("Total Runtime = ",end - start)
 


###Demo###

print(clean_data.head(20))

###Demo###

#Write to CSV
#clean_data.to_csv(f'{OUTPUT_LOCATION}/output.csv', index=False)

