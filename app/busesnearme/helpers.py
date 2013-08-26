from math import sqrt
import xml.etree.ElementTree as ET

import requests

from app import db

def stop_data(stop):
    """
    This method serializes a Stop object to a dictionary that can be
    converted to a json representation.
    """
    return {
        'id': stop.id,
        'lat': stop.lat,
        'lon': stop.lon,
        'tag': stop.tag,
        'title': stop.title,
        'stop_id': stop.stop_id}


def stop_data_from_row(row):
    """
    This method serializes row data from the Stops table to a dictionary
    that can be converted to a json representation.
    """
    return {
        'id': row[0],
        'lat': row[1],
        'lon': row[2],
        'tag': row[3],
        'title': row[4],
        'stop_id': row[5]}


def stops_near_point(lat, lon, distance):
    """
    This method returns a list of tuples containing stops that are within the
    specified `distance` of the input latitude-longitude coordinate.
    """
    result = db.session.execute(
        'select * from stops where '
        '{lat} between {min_lat} and {max_lat} and '
        '{lon} between {min_lon} and {max_lon}'.format(
            lat=lat, min_lat=(lat - distance), max_lat=(lat + distance),
            lon=lon, min_lon=(lon - distance), max_lon=(lon + distance)))

    filtered_stops = []
    for row in result.fetchall():
        stop_data = stop_data_from_row(row)
        candidate_distance = 69.0 * sqrt((stop_data['lat'] - lat) ** 2.0 +
                                         (stop_data['lon'] - lon) ** 2.0)
        if distance > candidate_distance:
            stop_data['distance'] = candidate_distance
            filtered_stops.append(stop_data)

    filtered_stops.sort(cmp=lambda s1,s2: cmp(s1['distance'], s2['distance']))
    return filtered_stops


def _api_url_511(method_name, **kwargs):
    query_string = '&'.join(['{0}={1}'.format(k, kwargs[k]) for k in kwargs])
    return ('http://services.my511.org/Transit2.0/'
            '{method_name}.aspx?{query}'.format(
         method_name=method_name, query=query_string))


def departures_at_stop(stop_id):
    """
    This method takes in a Stop and returns a list of routes that serve that
    stop with real-time departure times (if the route has any in the next
    hour).
    """
    TOKEN_511 = '7f140c33-acb1-4b15-b9b5-f9c80c421047'
    stop_departures_url = _api_url_511(
        'GetNextDeparturesByStopCode',
        token=TOKEN_511, stopcode=stop_id)

    stop_departures_request = requests.get(stop_departures_url)
    if 200 == stop_departures_request.status_code:
        root = ET.fromstring(stop_departures_request.text)
        listed_stops = []
        for agency in root.findall('./AgencyList/'):
            for route in agency.findall('./RouteList/'):
                for route_direction in route.findall('./RouteDirectionList/'):
                    for route_stop in route_direction.findall('./StopList/'):
                        departure_times = [departure.text for departure
                            in route_stop.findall('./DepartureTimeList/')]
                        if departure_times: 
                            listed_stops.append({
                                'stop_id': stop_id,
                                'name': route_stop.attrib.get('name'),
                                'route_direction':
                                    route_direction.attrib.get('Name'),
                                'route': route.attrib.get('Name'),
                                'departure_times': departure_times})
        return listed_stops
    else:
        return []
