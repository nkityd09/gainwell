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
nipyapi.security.service_login(service='nifi', username='ankity', password='Welcome1$')

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
    base64string = base64.b64encode(bytes('%s:%s' % ('ankity', 'Welcome1$'),'ascii'))
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
    base64string = base64.b64encode(bytes('%s:%s' % ('ankity', 'Welcome1$'),'ascii'))
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


# Root Path Testing
#root_path = get_names("9052312d-0187-1000-ffff-ffffb6cd1bee")
#root_path =nipyapi.canvas.recurse_flow("9052312d-0187-1000-ffff-ffffb6cd1bee")


# root_path = str(root_path)
# root_path = root_path.replace("None", "\"None\"")
# print(root_path)
# root_path = json.loads(root_path.replace("'", "\""))

# get_pg = nipyapi.canvas.get_flow("9052312d-0187-1000-ffff-ffffb6cd1bee")
# print(get_pg.process_group_flow.uri)

# print(get_root_path("8bc80698-0187-1000-0000-00005e7c549d"))







#queued_duration("8bcdb176-0187-1000-0000-00001cd6ea99")

#print(nipyapi.nifi.apis.flowfile_queues_api.FlowfileQueuesApi().get_flow_file(id = "8fc161ba-0187-1000-ffff-ffff9b1dd0a3", flowfile_uuid = "a61ef1ca-b156-47a2-8087-808639725c56", cluster_node_id = "e538f734-20dc-47b4-8934-5368281629e2"))
#print(nipyapi.nifi.models.flow_file_summary_dto.queued_duration("a61ef1ca-b156-47a2-8087-808639725c56"))














####Working Demo


# all_process_groups = nipyapi.canvas.list_all_process_groups()
# pg_id = []
# pg_name = []
# connection_id = []


# for pg in range(0, len(all_process_groups)):
#     pg_id.append(all_process_groups[pg].id)
#     pg_name.append(all_process_groups[pg].status.name)


# all_connections = nipyapi.canvas.list_all_connections(pg_id[-1])

# for conn_id in range(0, len(all_connections)):
#     connection_id.append(all_connections[conn_id].id)

# print(all_connections[1])




##### DataFrame Code #####

# pg_id_series = pd.Series(pg_id)
# pg_name_series = pd.Series(pg_name)
# connection_id_series = pd.Series(connection_id)

# clean_data = pd.DataFrame(columns = ['Process_Group_ID','Process_Group_Name', 'Connection_ID'])


# clean_data["Process_Group_ID"] = pg_id_series.values
# clean_data["Process_Group_Name"] = pg_name_series.values
# clean_data["Connection_ID"] = connection_id_series.values

# print(clean_data.head())

##### DataFrame Code #####


#Rough Code

#print(pg_id,"\n", pg_name, "\n", connection_id)

#Todo
#print(nipyapi.nifi.apis.flowfile_queues_api.FlowfileQueuesApi.create_flow_file_listing(id="8bcdb176-0187-1000-0000-00001cd6ea99"))

#nipyapi.nifi.models.flow_file_summary_dto.FlowFileSummaryDTO

# parent_pg_id = nipyapi.canvas.recurse_flow("8fc1e1aa-0187-1000-ffff-fffffe4d8a03")
# print(parent_pg_id.process_group_flow.parent_group_id)


# def get_names(pg_id):
#     get_pg = nipyapi.canvas.get_flow(pg_id)
#     json_string = str(get_pg.process_group_flow.breadcrumb)
#     print(json_string)
#     # parse the JSON string into a Python dictionary
#     data = json.loads(json_string)

#     # use a loop to navigate to the 'name' values
#     breadcrumb = data['breadcrumb']
#     name_values = []
#     while 'name' in breadcrumb:
#         name_values.append(breadcrumb['name'])
#         breadcrumb = breadcrumb.get('parent_breadcrumb', {})

#     # reverse the list to restore the original order
#     name_values.reverse()

#     # return the name values as a list
#     return name_values


# def recursive_function(previous_output):
    
#     final_path.append(previous_output)
#     # base case
#     if previous_output == root_id:
#         return final_path
    
#     parent_pg_id = nipyapi.canvas.recurse_flow(previous_output)
#     # recursive call
#     next_input = parent_pg_id.process_group_flow.parent_group_id
#     return recursive_function(next_input)