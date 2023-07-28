#!/usr/bin/bash

for f in $(ls modes)
do
	pip install -r modes/${f}/requirements.txt
done
