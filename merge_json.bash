#!/bin/bash

echo -n "["

# Because trailing commas in lists are not valid json, we handle the first file seperately
# then do the rest in a loop, inserting commas in between.
cat $1 | tail -c +2 | head -c -2

shift

for f in $@
do
	echo -n ", "
	cat $f | tail -c +2 | head -c -2
done

echo "]"
