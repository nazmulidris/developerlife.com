#!/bin/bash
for file in ../_posts/*
do
	# run doctoc on files that were modified (mmin) in the last 10 mins (-10)
	find "$file" -mmin -10 -exec doctoc "$file" \;
done