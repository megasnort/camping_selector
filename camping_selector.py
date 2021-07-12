import sys
import math
import xml.etree.ElementTree as ET
from html import escape

from geopy.distance import distance
from geopy import Point

def main():
    try:
        waypoints_files = sys.argv[1].split(',')
    except (IndexError, IOError):
        print('Give a valid input waypoint file')
        exit(1)

    try:
        route_files = sys.argv[2].split(',')
    except (IndexError, IOError):
        print('Give a valid input route file')
        exit(1)

    try:
        km_limit = abs(float(sys.argv[3]))
        skip = math.ceil(km_limit) * 15
        km_limit *= 1.1

    except (IndexError, IOError):
        print('Give a valid distance in km')
        exit(1)

    try:
        output_file = sys.argv[4]
    except (IndexError, IOError):
        print('Give a valid output file')
        exit(1)
    
    # fetch campings
    waypoints = []
    
    for waypoints_file in waypoints_files:
        print('Parsing', waypoints_file)
        tree = ET.parse(waypoints_file)
        root = tree.getroot()

        for child in root:
            lat = float(child.get('lat'))
            lon = float(child.get('lon'))
            name = child.find('{http://www.topografix.com/GPX/1/1}name').text

            waypoints.append({
                'lat': lat,
                'lon': lon,
                'name': name
            })

        print('Searching in set of', len(waypoints),'camping')

    # fetch routepoints
    route_points = []
    
    for route_file in route_files:
        print('Parsing', route_file)
        tree = ET.parse(route_file)
        root = tree.getroot()        

        trk = root.find('{http://www.topografix.com/GPX/1/1}trk')
        trksegs = trk.findall('{http://www.topografix.com/GPX/1/1}trkseg')
        trkpts = []
        
        for trkseg in trksegs:
            trkpts = trkpts + trkseg.findall('{http://www.topografix.com/GPX/1/1}trkpt')

        for trkpt in trkpts:
            route_points.append({
                'lat': trkpt.get('lat'),
                'lon': trkpt.get('lon')
            })

    print('Searching in set of', len(route_points),'routepoints.')
    print('Searching in reach of', km_limit,'km, skipping every', skip, 'routepoints.')

    output = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
    output += '<gpx creator="waypoint_selector" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1">\n'

    found = 0

    for waypoint in waypoints:
        counter = 0
        for route_point in route_points:
            if counter % skip == 0:
                km = distance(
                            Point(
                                waypoint['lat'],
                                waypoint['lon']
                            ),
                            Point(
                                route_point['lat'],
                                route_point['lon']
                            )
                        ).km
                if km < km_limit:
                    output += '<wpt lat="' + str(waypoint['lat']) + '" lon="' + str(waypoint['lon']) + '"><name>' + escape(waypoint['name']) + '</name></wpt>\n'
                    print(waypoint['name'], waypoint['lat'], waypoint['lon'], km)
                    found += 1
                    break
            counter += 1

    output += '</gpx>'


    with open(output_file, 'w') as f:
        f.write(output)

    print(found,'campings found.')

if __name__ == '__main__':
    main()
