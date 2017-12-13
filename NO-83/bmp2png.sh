#!/bin/bash

for bmp_file in *.bmp;
do
  png_file="${bmp_file:0: -4}.png"
  echo "Converting $bmp_file to $png_file"
  convert "$bmp_file" "$png_file"
  echo "Deleting $bmp_file"
  rm $bmp_file
done

exit $?
