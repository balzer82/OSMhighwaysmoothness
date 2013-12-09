#!/bin/bash
echo "Konvertiere .pbf in .o5m"
./osmconvert deutschland/germany-latest.osm.pbf -o=deutschland/germany.o5m
echo "pruning map"
./osmfilter deutschland/germany.o5m --keep="smoothness=good =bad =intermediate =excellent =very_bad =horrible =very_horrible admin_level=2 place=city and population>=500000" -o=deutschland/germany-smoothnesstag.o5m
echo "Konvertiere .o5m in .pbf"
./osmconvert deutschland/germany-smoothnesstag.o5m -o=deutschland/germany-smoothnesstag.osm.pbf
echo "Cleaning up"
rm deutschland/germany-smoothnesstag.o5m
rm deutschland/germany.o5m
echo "done."