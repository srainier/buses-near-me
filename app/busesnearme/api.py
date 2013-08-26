from flask import jsonify, request
from geopy.geocoders.googlev3 import GoogleV3, GQueryError
from geopy.geocoders.base import GeocoderResultError

from app import app
from app.busesnearme.helpers import (departures_at_stop, stop_data,
                                     stops_near_point)
from app.busesnearme.models import Stop


@app.route('/stops/<int:stop_id>')
def get_stop(stop_id):
    """
    This method returns data about a stop with the specified stop_id (the
    stopcode used by the transit agencies).
    """
    stop = Stop.query.filter_by(stop_id=stop_id).first()
    if stop:
        return jsonify(stop_data(stop))
    else:
        return jsonify({'error': 'no stop with id {0}'.format(stop_id)})


@app.route('/stops/<coord:lat>,<coord:lon>')
def get_stops(lat, lon):
    """
    This method returns a list of stops near the specified latitude-longitude
    coordinates. This method can optionally specify a maximum distance (in 
    miles) a stop can be from the input coordinates. If none is specified the
    default is 1 mile.
    """
    distance = 1.0
    distance_list = request.args.getlist('distance')
    if 0 < len(distance_list):
        distance = float(distance_list[0])

    stops = stops_near_point(lat, lon, distance)
    if stops:
        return jsonify({'stops': [stop for stop in stops]})

    return jsonify({'error': 'No stops near ({0}, {1})'.format(lat, lon)})


@app.route('/stops/<int:stop_id>/departures')
def get_departures_at_stop(stop_id):
    """
    This method returns a list of departures times for routes with departures
    from the specified stop as given by the 511.org real-time departure api
    (http://511.org/developer-resources_transit-api.asp).
    """
    stop = Stop.query.filter_by(stop_id=stop_id).first()
    if stop:
        return jsonify({'departures': departures_at_stop(stop.stop_id)})

    return jsonify({'error': 'no stop with id {0}'.format(stop_id)})


@app.route('/stops/<coord:lat>,<coord:lon>/departures')
def get_departures(lat, lon):
    """
    This method returns a list of departures times for routes with departures
    from stops near the specified latitude-longitude coordinates as given by
    the 511.org real-time departure api
    (http://511.org/developer-resources_transit-api.asp).
    This method can optionally specify a maximum distance (in miles) a stop can
    be from the input coordinates. If none is specified the default is 1 mile.
    """
    # This method can optionally specify a maximum distance a stop can
    # be from the input coordinates.
    distance = 1.0
    distance_list = request.args.getlist('distance')
    if 0 < len(distance_list):
        distance = float(distance_list[0])

    stops = stops_near_point(lat, lon, distance)
    if stops:
        departures = [departures_at_stop(stop['stop_id']) for stop in stops]
        return jsonify({'departures': departures})

    return jsonify({'error': 'No stops near ({0}, {1})'.format(lat, lon)})


@app.route('/locate/')
def locate():
    """
    This method uses the Google Maps v3 API to convert and input query string
    into latitude-longitude coordinates and a string summary.
    This method will only return valid positional data if the Google Maps API
    call returns a single result (i.e. the query wasn't too vague and referred
    to a valid location).
    """
    query_list = request.args.getlist('query')
    if 0 < len(query_list):
        # Just take the first one
        query = query_list[0]

        # Plug the query into geopy's Google geolocator and see if we get a
        # unique result.
        g = GoogleV3()
        try:
            place, (lat, lon) = g.geocode(query)
            return jsonify({
                'place': place,
                'lat': lat,
                'lon': lon })
        except ValueError:
            return jsonify({'error': 'multiple results'})
        except GQueryError:
            return jsonify({'error': 'no results'})
        except GeocoderResultError:
            return jsonify({'error': 'unknown'})

    return jsonify({'error': 'no query'})
