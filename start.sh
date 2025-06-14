#!/bin/bash

# Get an absolute path to the script
basedir=$(dirname $0)
absdir=$(realpath -s "${PWD}/${basedir}")

if [ -d "${absdir}/.venv" ]; then
  echo "${absdir}/.venv exists - removing and resetting"
  rm -rf "${absdir}/.venv"
fi

pythoncmd=python3 # TODO: this might need to be changed?

$pythoncmd -m venv "${absdir}/.venv"
echo "Made venv successfully"

source "${absdir}/.venv/bin/activate"
echo "Activated venv successfully"

# Re-assess the python command now that we're in the venv
pythoncmd=$(command -v python) || $(command -v python3)

$pythoncmd -m pip install -r "${absdir}/requirements.txt" >/dev/null 2>&1
echo "Installed Python requirements successfully"

cd "${absdir}/src"
echo "Starting up.."
$pythoncmd __main__.py
