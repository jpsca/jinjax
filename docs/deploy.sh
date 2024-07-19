#!/bin/bash
python docs.py build
ssh code 'rm -rf /var/www/jinjax/build'
rsync --recursive --delete --progress build code:/var/www/jinjax/
