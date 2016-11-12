import json


# es query for tweets in specific location
def search_query(latitude, longitude, distance, search_key=''):
    if search_key:
        return json.dumps({
                "size": 250,
                "sort" : [
                            { "score" : {"order" : "desc"}}
                        ],
                "query": 
                    { "bool" : 
                        { "must" : 
                            { "match": {"text": "{search_key}".format(search_key=search_key)}
                        }, "filter" : 
                            {"geo_distance" : 
                                {"distance" : 
                                    "{distance}km".format(distance=distance), 
                                    "location" : 
                                        "{latitude}, {longitude}"
                                        .format(latitude=latitude, 
                                            longitude=longitude)
                                }
                            }
                        }
                    }
                })
    else:
        return json.dumps({
                "size": 250,
                "sort" : [
                            { "score" : {"order" : "desc"}}
                        ],
                "query": 
                    { "bool" : 
                        { "must" : 
                            { "match_all": {}
                        }, "filter" : 
                            {"geo_distance" : 
                                {"distance" : 
                                    "{distance}km".format(distance=distance), 
                                    "location" : 
                                        "{latitude}, {longitude}"
                                        .format(latitude=latitude, 
                                            longitude=longitude)
                                }
                            }
                        }
                    }
                })
