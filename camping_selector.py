import sys
import math
import xml.etree.ElementTree as ET
from html import escape


from geopy import Point, distance

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
    
    # fetch routepoints
    route_points = []
    smallest_lat = 1000000
    smallest_lon = 1000000
    greatest_lat = -1000000
    greatest_lon = -1000000

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
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            
            route_points.append({
                'lat': lat,
                'lon': lon
            })

            if lat < smallest_lat:
                smallest_lat = lat
            if lat > greatest_lat:
                greatest_lat = lat
    
            if lon < smallest_lon:
                smallest_lon = lon
            if lon > greatest_lon:
                greatest_lon = lon

    SW = Point(smallest_lat, smallest_lon)
    NE = Point(greatest_lat, greatest_lon)

    d = distance.distance(kilometers=km_limit)
    NE = d.destination(point=NE, bearing=45)
    SW = d.destination(point=SW, bearing=225)

    print('Searching in set of', len(route_points),'routepoints.')
    
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

            if SW[0] <= lat <= NE[0] and SW[1] <= lon <= NE[1]:
                waypoints.append({
                    'lat': lat,
                    'lon': lon,
                    'name': name
                })


    print('Searching in set of', len(waypoints),'campings')

    

    output = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
    output += '<gpx creator="waypoint_selector" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1">\n'

    found = 0

    for waypoint in waypoints:
        counter = 0
        for route_point in route_points:
            if counter % skip == 0:
                km = distance.distance(
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
    