#!/bin/bash
python docs.py build
rsync --recursive --delete --progress build code:/var/www/jinjax/
