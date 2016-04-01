from bottle import route, run
import geopandas as gp
import networkx as nx
from shapely.geometry import  MultiLineString, mapping

walkspeed = 16368 # ft/h

# Load shapefile
shp = gp.GeoDataFrame.from_file('lionStreets/lionStreets.shp')

# Create Network
n = nx.Graph()
for r in shp[['NodeIDFrom', 'NodeIDTo', 'SHAPE_Leng', 'RW_TYPE', 'Street', 'geometry']].iterrows():
    n.add_edge(r[1]['NodeIDFrom'], r[1]['NodeIDTo'], attr_dict={
        'type': r[1]['RW_TYPE'],
        'len': r[1]['SHAPE_Leng'],
        'name': r[1]['Street'],
        'geo': r[1]['geometry']
    })

# Walkshed from node + time in minutes
@route('/walkshed/time/<node>/<time>')
def walkshedtime(node, time):
    dist = walkspeed * (float(time)/60)
    return walkshed(node, dist)

# walkshed from node + dist in feet
@route('/walkshed/dist/<node>/<dist>')
def walksheddist(node, dist):
    return walkshed(node, float(dist))

def walkshed(start, dist):
    visited = []
    queued = [start]
    to_visit = [(start, 0)] # node, dist at node
    lines = []

    while to_visit:
        node,cur_dist = to_visit.pop()
        edges = n.edges(nbunch=[node], data=True)
        for e in edges:
            if e[2]['type'] in ['1', '5', '6', '10']:
                if cur_dist + e[2]['len'] < dist:
                    if e[2]['geo'] not in lines:
                        lines.append(e[2]['geo'])
                    if e[1] not in queued:
                        to_visit.append((e[1], cur_dist + e[2]['len']))
                        queued.append(e[1])

    return mapping(MultiLineString(lines))

run(host='localhost', port=1337 )
