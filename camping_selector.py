import sys
import xml.etree.ElementTree as ET
from html import escape

from geopy.distance import distance
from geopy import Point

def main():
    try:
        waypoints_file = sys.argv[1]
    except (IndexError, IOError):
        print('Give a valid input waypoint file')
        exit(1)

    try:
        route_file = sys.argv[2]
    except (IndexError, IOError):
        print('Give a valid input route file')
        exit(1)

    try:
        km_limit = float(sys.argv[3])
    except (IndexError, IOError):
        print('Give a valid distance in km')
        exit(1)

    try:
        output_file = sys.argv[4]
    except (IndexError, IOError):
        print('Give a valid output file')
        exit(1)

    # parse routepoints per factor. By average, routepoints are about 40m apart.
    # A factor of 10 will check per 400m for a campsite. The lower the factor, the slower the script.
    try:
        factor = int(sys.argv[5])
    except (IndexError, IOError):
        factor = 200
        
    
    factor

    # fetch campings
    tree = ET.parse(waypoints_file)
    root = tree.getroot()

    waypoints = []

    for child in root:
        lat = float(child.get('lat'))
        lon = float(child.get('lon'))
        name = child.find('{http://www.topografix.com/GPX/1/1}name').text

        waypoints.append({
            'lat': lat,
            'lon': lon,
            'name': name
        })

    print('Searching in set of', len(waypoints),'campsites')

    # fetch routepoints
    tree = ET.parse(route_file)
    root = tree.getroot()

    route_points = []

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

    output = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
    output += '<gpx creator="waypoint_selector" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1">\n'

    found = 0

    for waypoint in waypoints:
        counter = 0
        for route_point in route_points:
            if counter % factor == 0:
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

    print(found,'campsites found.')

if __name__ == '__main__':
    main()
