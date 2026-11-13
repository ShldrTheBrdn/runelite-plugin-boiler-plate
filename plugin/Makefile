.PHONY: help build run update

help:
	@echo '  make build   Build the plugin'
	@echo '  make run     Launch RuneLite with the plugin'
	@echo '  make update  Fetch the latest flake.nix and flake.lock'

build run:
	gradle --no-daemon --console=plain $@

update:
	python3 scripts/project.py update
