from flask_googlemaps import Map
def marked_map(results):
	markers_list = []
	for result in results:
		print result[u'_source'][u'location'][u'lat']
		markers_list.append( {'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
						'lat': int(result[u'_source'][u'location'][u'lat']),
						'lon': int(result[u'_source'][u'location'][u'lon']),
						'infobox': "<b>" + result[u'_source'][u'text'] + "</b>"
						})		
	return Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=markers_list
    )
