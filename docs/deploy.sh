#!/bin/bash
rm -rf build
uv run python docs.py build --llm
rsync --recursive --delete --progress build code:/var/www/jinjax/
