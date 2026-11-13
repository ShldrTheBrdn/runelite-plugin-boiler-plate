.PHONY: help init

help:
	@echo '  make init                  Ask for a name and create a sibling repository'
	@echo '  make init NAME="My Plugin"  Create a plugin without prompting'

init:
	python3 scripts/project/init_plugin.py