from flask_googlemaps import Map
def marked_map(data, latitude, longitude):
	markers_list = []
	for item in data:
		markers_list.append( {'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
						'lat': float(item[u'location'][u'lat']),
						'lng': float(item[u'location'] [u'lon']),
						'infobox': '<b>' + item[u'text'] + '</b>'
						})		
	return Map(
        identifier="sndmap",
        lat=float(latitude),
        lng=float(longitude),
        markers=markers_list
    )
