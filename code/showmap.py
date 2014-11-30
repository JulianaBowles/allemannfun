#!/usr/bin/env python
import codecs
import argparse
from geopy.geocoders import Nominatim
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy

geolocator = Nominatim(timeout=10)

parser = argparse.ArgumentParser()
parser.add_argument("list",metavar='FILE',help="file containing a list of locations")
args = parser.parse_args()

lons = []
lats = []
with codecs.open(args.list,'r', 'utf-8') as inlist:
    for line in inlist.readlines():
        location = geolocator.geocode(line.strip())
        if location == None:
            print 'Warning, cannot find: ',line.strip()
        lons.append(location.longitude)
        lats.append(location.latitude)

m = Basemap(llcrnrlon=4,llcrnrlat=46,urcrnrlon=18,urcrnrlat=55,
            resolution='i',projection='tmerc',lon_0=11,lat_0=50.5)
#m.drawrivers(color='b')
m.fillcontinents(color='coral',lake_color='aqua',zorder=0)
m.drawcoastlines()
m.drawcountries()
# draw parallels and meridians.
m.drawparallels(numpy.arange(-40,61.,2.))
m.drawmeridians(numpy.arange(-20.,21.,2.))
m.drawmapboundary(fill_color='aqua')
# show where people are from
m.scatter(lons,lats,latlon=True,marker='o',color='k')


plt.show()
