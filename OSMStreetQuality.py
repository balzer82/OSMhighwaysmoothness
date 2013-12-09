# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#
# http://dataorigami.blogspot.de/2010/10/beta-release-how-to-render.html
#
#
#############################################################
## from http://code.activestate.com/recipes/534109-xml-to-python-data-structure
 
import re
import xml.sax.handler
from xml.dom.minidom import parse
import json
import sys
import os
import numpy as np
import requests
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# <headingcell level=1>

# Map rendern

# <headingcell level=3>

# Farbcodes, Stadtteile, Startpunkt

# <codecell>

def render(myMap, subfolder, minX, maxX, minY, maxY):
 
    # make dictionary of node IDs
    nodes = {}
    for node in myMap['node']:
        nodes[node['id']] = node
         
    ways = {}
    for way in myMap['way']:
        ways[way['id']]=way
    
    orange = (255.0/255,103.0/255,0.0/255)
    dunkelgruen = (113.0/255,104.0/255,90.0/255)
    dunkelgrau = (113.0/255,104.0/255,90.0/255)
    blau = (0.0/255,0.0/255,128.0/255)
 
    renderingRules = {
        'motorway': dict(
                linestyle       = '-',
                linewidth       = 4,
                color           = dunkelgruen, 
                zorder          = -1,
                ),
        'primary': dict(
                linestyle       = '-',
                linewidth       = 2,
                color           = dunkelgruen, 
                zorder          = -2,
                ),
        'primary_link': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgruen,
                zorder          = -2,            
                ),
        'secondary': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgrau,
                zorder          = -3,            
                ),
        'secondary_link': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgrau,
                zorder          = -3,            
                ),
        'tertiary': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgrau,
                zorder          = -4,            
                ),
        'tertiary_link': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgrau,
                zorder          = -4,            
                ),
        'residential': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgrau,
                zorder          = -5,            
                ),            
        'unclassified': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgrau,
                zorder          = -5,            
                ),
        'default': dict(
                linestyle       = '-',
                linewidth       = 1,
                color           = dunkelgrau,
                zorder          = -5,            
                ),
        }
                         
 
    # get bounds from OSM data            
    '''
    minX = float(myMap['bounds']['minlon'])
    maxX = float(myMap['bounds']['maxlon'])
    minY = float(myMap['bounds']['minlat'])
    maxY = float(myMap['bounds']['maxlat'])
    '''

    fig = plt.figure(figsize=(12,16))
    
    ax = fig.add_subplot(111,autoscale_on=False,xlim=(minX+0.01,maxX-0.01),ylim=(minY+0.01,maxY-0.01))
    ax.set_xticks([]) 
    ax.set_yticks([]) 
    
    
    # by setting limits before hand, plotting is about 3 times faster
    #ax = fig.add_subplot(111,autoscale_on=False,xlim=(minX,maxX),ylim=(minY,maxY))
    for idx,nodeID in enumerate(ways.keys()):        
 
        wayTags         = ways[nodeID]['tag']
        if not wayTags==None:
            hwyTypeList  = [d['v'] for d in wayTags if d['k']=='highway' or d['k']=='waterway']
            if len(hwyTypeList)>0:
                    wayType = hwyTypeList[0]  
            else:
                    wayType = None
        else:
            wayType = None
        try:
            if wayType in ['primary','primary_link',
                            'unclassified',
                            'secondary','secondary_link',
                            'tertiary','tertiary_link',
                            'residential',
                            'trunk','trunk_link',
                            'motorway','motorway_link',
                            'river','riverbank',
                            ]:
                oldX = None
                oldY = None
                 
                if wayType in renderingRules.keys():
                    thisRendering = renderingRules[wayType]
                else:
                    thisRendering = renderingRules['default']
                     
                for nCnt,nID in enumerate(ways[nodeID]['nd']):
                    y = float(nodes[nID['ref']]['lat'])
                    x = float(nodes[nID['ref']]['lon'])
                    if oldX == None:
                        pass
                    else:
                        plt.plot([oldX,x],[oldY,y],
                            marker          = '',
                            linestyle       = thisRendering['linestyle'],
                            linewidth       = thisRendering['linewidth'],
                            color           = thisRendering['color'],
                            solid_capstyle  = 'round',
                            solid_joinstyle = 'round',
                            zorder          = thisRendering['zorder'],
                            )
                    oldX = x
                    oldY = y
                        
        except KeyError:
            pass

    return plt

# <headingcell level=1>

# XML zu Python Objekt

# <codecell>

def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """
 
    non_id_char = re.compile('[^_0-9a-zA-Z]')
    def _name_mangle(name):
        return non_id_char.sub('_', name)
 
    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data
        def __len__(self):
            # treat single element as a list of 1
            return 1
        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key,None)
            else:
                return [self][key]
        def __contains__(self, name):
            return self._attrs.has_key(name)
        def __nonzero__(self):
            return bool(self._attrs or self.data)
        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)
        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value
        def __str__(self):
            return self.data or ''
        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])
 
    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr(_name_mangle(k), v)
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)
        def characters(self, content):
            self.text_parts.append(content)
 
    builder = TreeBuilder()
    if isinstance(src,basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]

# <headingcell level=2>

# Main

# <codecell>

subfolder = u'deutschland'
name = u'germany-smoothnesstag'

# Bounds von http://boundingbox.klokantech.com/ holen
bounds = [5.85,47.22,15.06,54.94]
maxY = bounds[3]
maxX = bounds[2]
minY = bounds[1]
minX = bounds[0]

########################################
try:
    with open(subfolder + '/' + name + '.osm'):
        print('Lade .osm File.')
        src = file(subfolder + '/' + name + '.osm')
    print 'OSM Datei eingelesen'
except IOError:
    print 'No .osm file found.'

    
myMap = xml2obj(src)
print('Objekt eingelesen.')

# <headingcell level=3>

# Interpolieren und Karte rendern

# <codecell>

render(myMap, subfolder, minX, maxX, minY, maxY)
print('Map gerendert.')

# <headingcell level=3>

# Map abspeichern

# <codecell>

pdfoutfile = subfolder + '/' + name + '.pdf'
pngoutfile = subfolder + '/' + name + '.png'
plt.savefig(pdfoutfile, dpi=150, facecolor='w', edgecolor='w',
            papertype=None, format=None,
            transparent=False, bbox_inches='tight', pad_inches=0.1,
            frameon=None)
plt.savefig(pngoutfile, dpi=150, facecolor='w', edgecolor='w',
            papertype=None, format=None,
            transparent=False, bbox_inches='tight', pad_inches=0.1,
            frameon=None)
print('Karten unter \'' + pdfoutfile + '\' und \'' + pngoutfile + '\' abgespeichert.')
#plt.show()

# <codecell>

plt.close()

