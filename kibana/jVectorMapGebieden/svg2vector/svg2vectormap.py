
from xml.dom import minidom

dirPath = '../public/'
fileName = 'gbd_buurt.svg'

xmldoc = minidom.parse(fileName)
itemlist = xmldoc.getElementsByTagName('g')
print(len(itemlist))

pathItem = {}
paths = {}

item = itemlist[3]

print(item.toxml())
print(item.attributes.keys())

# Get ID value

for item in itemlist:
	try:
		idPolygon = str(item.attributes['inkscape:label'].value)
		if idPolygon != 'qgisviewbox':
			print(idPolygon)

			# Get geometry
			path = item.getElementsByTagName("path")
			for d in path:
			    polygon = str(d.attributes['d'].value).replace(" ","")
			    print(polygon)

			pathItem[idPolygon]= { "path" : polygon }
			pathItem[idPolygon]['name'] = idPolygon
			print(pathItem)

			paths.update(pathItem)
	except:
		continue

stringText = """jQuery.fn.vectorMap('addMap', 'buurt_mill',
		{"insets": [{"width": 900, 
				 "height": 790.3360148034734,
				 "top": 0,
				 "left": 0, 
				 "bbox": [{"y": -9690291.808548316, "x": -4159652.5301950974},
						 {"y": -3201145.6268246872, "x": 3229902.613642692}]
				}], 
			"paths": %s,
			"height": 790, 
			"width": 900,
			"projection": {"type": "mill", "centralMeridian": 11.5}
			});""" % paths

print(stringText)

with open(dirPath+'jquery-jvectormap-buurt-mill.js', 'w') as buurt:
	buurt.write(stringText)