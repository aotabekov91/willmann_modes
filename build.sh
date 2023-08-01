#!/usr/bin/bash

for f in $(ls src/modes)
do
	pip install -r src/modes/${f}/requirements.txt
done
