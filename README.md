# OSMhighwaysmoothness

## Wofür?

Filtert aus [Openstreetmaps .osm.pbf](http://download.geofabrik.de/europe/germany.html) alle Straßen (highways) heraus, welche einen [smoothness tag](http://taginfo.openstreetmap.org/keys/smoothness) haben.

![Deutschlands Straßen mit Smoothness-Tag](https://raw.github.com/balzer82/OSMhighwaysmoothness/master/germany-smoothnesstag.png)


## Wie benutzt man es?

1. gewünschte Karte im .osm.pbf Format [downloaden](http://download.geofabrik.de/europe/germany.html)
2. im Terminal `./osm-edit.sh` eingeben
3. im Terminal `python OSMStreetQuality.py eingeben`

## Was tut es?

1. konvertiert die .osm.pbf in .o5m
2. filtert alles heraus, was nicht `smoothness=` als Tag hat
3. rendert Karte

## Dependencies

1. Matplotlib (for Rendering)
2. numpy (for array)
3. xml.dom (for .osm)
3. [osmconvert](http://wiki.openstreetmap.org/wiki/Osmconvert)
4. [osmfilter](http://wiki.openstreetmap.org/wiki/DE:Osmfilter)

