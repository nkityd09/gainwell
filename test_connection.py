import nipyapi
from nipyapi import canvas,config
import urllib
import pandas as pd
import json
import base64
import datetime

nipyapi.config.nifi_config.force_basic_auth = True

#Variables
nifi_endpoint = "https://test-nifi-management0.epsilon.a465-9q4k.cloudera.site/test-nifi/cdp-proxy-api/nifi-app/nifi-api"
#Setup environement
nipyapi.utils.set_endpoint(nifi_endpoint)
#Login to Nifi Service
nipyapi.security.service_login(service='nifi', username='ankity', password='Password')

root_id = canvas.get_root_pg_id()
all_connections = nipyapi.canvas.list_all_connections(root_id)
all_process_groups = nipyapi.canvas.list_all_process_groups()



def get_pg_name(pg_id):
    get_pg = nipyapi.canvas.get_flow(pg_id)
    return get_pg.process_group_flow.breadcrumb.breadcrumb.name

#TODO Format Root Path
#Get Root Path
def get_names(pg_id):
    get_pg = nipyapi.canvas.get_flow(pg_id)
    data = get_pg.process_group_flow.breadcrumb
    # breadcrumb = data.breadcrumb
    # name_values = []
    # while 'name' in breadcrumb:
    #     name_values.append(breadcrumb['name'])
    #     breadcrumb = breadcrumb.get('parent_breadcrumb', {})

    return data

def queued_duration(connection_id):
    listing_requests = nipyapi.nifi.apis.flowfile_queues_api.FlowfileQueuesApi().create_flow_file_listing(connection_id)
    request = urllib.request.Request(listing_requests.listing_request.uri)
    base64string = base64.b64encode(bytes('%s:%s' % ('ankity', 'Password'),'ascii'))
    request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
    with urllib.request.urlopen(request) as url:
        data = json.load(url)
    queued_duration = data["listingRequest"]["flowFileSummaries"][0]["queuedDuration"]
    delta = datetime.timedelta(milliseconds=queued_duration)
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
    get_pg = nipyapi.canvas.get_flow(pg_id)
    request = urllib.request.Request(get_pg.process_group_flow.uri)
    base64string = base64.b64encode(bytes('%s:%s' % ('ankity', 'Password'),'ascii'))
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
#root_path = []

for conns in range(0, len(all_connections)):
    pg_id.append(all_connections[conns].source_group_id)
    connection_id.append(all_connections[conns].id)
    flow_count.append(all_connections[conns].status.aggregate_snapshot.queued_count)
    

#Dataframe setup
final_path = []
pg_id_series = pd.Series(pg_id)
connection_id_series = pd.Series(connection_id)
flow_count_series = pd.Series(flow_count)
clean_data = pd.DataFrame(columns = ['Process_Group_Name', 'Process_Group_ID', 'Connection_ID', 'Flow_File_Count','Max_Queued_Duration', 'Root_path'])
clean_data["Process_Group_ID"] = pg_id_series.values
clean_data["Process_Group_Name"] = clean_data['Process_Group_ID'].apply(get_pg_name)
clean_data["Connection_ID"] = connection_id_series.values
clean_data["Flow_File_Count"] = flow_count_series.values
clean_data["Root_path"] = clean_data['Process_Group_ID'].apply(get_root_path)
clean_data["Max_Queued_Duration"] = clean_data['Connection_ID'].apply(queued_duration)

###Demo###

print(clean_data.head(10))

###Demo###

##Output##
#
#  Process_Group_Name                      Process_Group_ID                         Connection_ID Flow_File_Count  Max_Queued_Duration                                          Root_path
#0       level4_group  9052312d-0187-1000-ffff-ffffb6cd1bee  905340f3-0187-1000-ffff-ffff8a99c393          29,553             6.951988  [level4_group, level3_group, alpha_group, NiFi...
#1       level3_group  8fc1e1aa-0187-1000-ffff-fffffe4d8a03  8fc23f1d-0187-1000-0000-00004315b29e          30,000             7.061849             [level3_group, alpha_group, NiFi Flow]
#2       level3_group  8fc1e1aa-0187-1000-ffff-fffffe4d8a03  8fc26bb9-0187-1000-ffff-ffffba727462          30,000             7.061854             [level3_group, alpha_group, NiFi Flow]
#3        alpha_group  8fc0df69-0187-1000-ffff-ffffd3062a16  8fc161ba-0187-1000-ffff-ffff9b1dd0a3          30,000             7.062615                           [alpha_group, NiFi Flow]
#4         beta_group  8fc12123-0187-1000-0000-0000227fadce  8fc4d311-0187-1000-ffff-ffffe5b969aa          30,000             7.060035                            [beta_group, NiFi Flow]
#5              dummy  8bc80698-0187-1000-0000-00005e7c549d  8bcdb176-0187-1000-0000-00001cd6ea99          30,000             7.509054                                 [dummy, NiFi Flow]
#6              dummy  8bc80698-0187-1000-0000-00005e7c549d  95cd1a1c-0187-1000-0000-00002bc6700a          22,998             5.888641                                 [dummy, NiFi Flow]
##Output##