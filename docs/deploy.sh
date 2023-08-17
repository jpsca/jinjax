#!/bin/bash
npm run build
python docs.py build
rsync --recursive --delete --progress build code:/var/www/jinjax/
