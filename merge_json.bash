#!/bin/bash

echo -n "["

if [ -s "${@:1}" ]
then
	cat "${@:1}" | tail -c +2 | head -c -2
fi

shift

for f in "$@"
do
	if [ -s $f ]
	then
		echo -n ", "
		cat $f | tail -c +2 | head -c -2
	fi
done

echo "]"
