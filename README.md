# RuneLite Plugin Boilerplate

Reusable project infrastructure and a small working plugin scaffold. Each plugin
gets its own Git repository and complete Nix environment for development containing all necessary dependencies.

## Project Structure

The boilerplate and generated plugins live alongside each other:

```text
runelite-plugin-boiler-plate/
├── Makefile            Creates new plugins
├── make/               Separate initialization and plugin Make targets
├── templates/          Starter plugin files
├── scripts/            Project creation and update logic
├── project-files.json  Shared files copied into new plugins
├── flake.nix           Development environment
└── ...
plugin-1/
├── Makefile            Builds, runs, and updates this plugin
├── src/                Plugin source and development launcher
├── plugin.json         Plugin identity
├── flake.nix           Independent development environment
└── ...
```

Run `make init` from `runelite-plugin-boiler-plate` to create a plugin.
Inside each generated plugin, use `make build`, `make run`, and `make update`.

Each plugin has its own Git repository and development environment.
Shared tooling updates come from `runelite-plugin-boiler-plate`.

## Dependencies

Install these tools on your host:

- Make
- Python 3
- Git
- Nix

`make init` checks all dependencies before creating a plugin. `make build` and
`make run` use Java and Gradle from your current environment. Enter `nix develop`
to load them, or install Java 11 and Gradle 8 directly; these commands do not
require Nix.

To check dependencies separately, run `sh scripts/check-dependencies.sh`.

## Creating a New Plugin

## Updating Existing Plugins

Run inside a generated plugin:

```sh
make update
```

This temporarily clones the latest default branch of
[runelite-plugin-boiler-plate](https://github.com/ShldrTheBrdn/runelite-plugin-boiler-plate)
over HTTPS and updates only `flake.nix` and `flake.lock` from the same commit.
Python 3 and Git are required. A local boilerplate checkout is not needed.

Replaced files are backed up under `.boilerplate-backups/`, and changes are left
unstaged. Conflicting local edits stop the update before any files are replaced.
Use `make update FORCE=1` to accept the upstream versions with backups.
