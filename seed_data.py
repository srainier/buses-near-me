import requests
import xml.etree.ElementTree as ET
import yaml

AGENCIES = [{'title': 'sf-muni'}, {'title': 'actransit'}]

def generate_table_data(filename="stops.yaml"):
    """
    This method uses the nextbus API to generate a list of stops for the
    transit agencies in AGENCIES above. This data can be used to seed the
    Stops table for busesnearme.
    """
    stops = {}
    for agency in AGENCIES:
        # Get the agency's routes
        route_list_api_url = ('http://webservices.nextbus.com/service/'
                              'publicXMLFeed?command=routeList'
                              '&a={agency}'.format(agency=agency['title']))
        route_list_request = requests.get(route_list_api_url)
        if route_list_request.status_code != 200:
            continue

        route_list_root = ET.fromstring(route_list_request.text)
        for route in route_list_root.findall('./route'):
            route_stops_url = ('http://webservices.nextbus.com/service/'
                               'publicXMLFeed?command=routeConfig'
                               '&a={agency}&r={route}'.format(
                                   agency=agency['title'],
                                   route=route.attrib['tag']))
            route_stops_request = requests.get(route_stops_url)
            if 200 != route_stops_request.status_code:
                continue
            
            route_stops_root = ET.fromstring(route_stops_request.text)
            for stop in route_stops_root.findall('./route/stop'):
                if not 'stopId' in stop.attrib:
                    continue
                stop_id = int(stop.attrib['stopId'])
                
                if not stop_id in stops:
                    stops[stop_id] = {
                        'tag': int(stop.attrib['tag']),
                        'title': str(stop.attrib['title']),
                        'lat': float(stop.attrib['lat']),
                        'lon': float(stop.attrib['lon']),
                        'stop_id': int(stop.attrib['stopId'])}
                        
    with open(filename, "w") as f:
        f.write(yaml.dump({'stops': stops.values()}))

    
def create_csv_data(filename="stops.yaml"):
    """
    This method will take in file written out by generate_table_data and
    write out an equivalent comma-separated values file. This can be used to
    seed a test sqlite3 database.
    """
    with open(filename, "r") as f:
        stops = yaml.load(f.read())
    
    with open("stops.csv", "w") as f:
        for index, stop in enumerate(stops['stops']):
            f.write('{id}, {lat}, {lon}, {tag}, {title}, {stop_id}\n'.format(
                id=index + 1, **stop))
