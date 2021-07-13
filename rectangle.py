import sys
import xml.etree.ElementTree as ET
from html import escape

# very simple first version of the program that
# selects the waypoints between two
# coordinates.

def main():
    try:
        input_file = sys.argv[1]
    except (IndexError, IOError):
        print('Give a valid input file')
        exit(1)

    try:
        coor1 = [float(i) for i in sys.argv[2].split(',')]
    except (IndexError, IOError):
        print('Give a valid coordinate: 0.000000,0.000000')
        exit(1)

    try:
        coor2 = [float(i) for i in sys.argv[3].split(',')]
    except (IndexError, IOError):
        print('Give a valid second coordinate: 0.000000,0.000000')
        exit(1)

    try:
        output_file = sys.argv[4]
    except (IndexError, IOError):
        print('Give a valid output file')
        exit(1)


    # put smaller values in front, to make comparing later easier
    if coor1[0] > coor2[0]:
        coor1[0], coor2[0] = coor2[0], coor1[0]
    
    if coor1[1] > coor2[1]:
        coor1[1], coor2[1] = coor2[1], coor1[1]


    print('Fetching all waypoints between', coor1, 'and', coor2)


    tree = ET.parse(input_file)
    root = tree.getroot()

    output = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
    output += '<gpx creator="waypoint_selector" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1">\n'

    for child in root:
        lat = float(child.get('lat'))
        lon = float(child.get('lon'))

        if coor1[0] <= lon <= coor2[0] and coor1[1] <= lat <= coor2[1]:
            name = child.find('{http://www.topografix.com/GPX/1/1}name').text
            print(name, lat, lon)
            name = escape(name)
            output += '<wpt lat="' + str(lat) + '" lon="' + str(lon) + '"><name>' + name + '</name></wpt>\n'

    output += '</gpx>'

    with open(output_file, 'w') as f:
        f.write(output)

if __name__ == '__main__':
    main()
