#!/usr/bin/env bash

# activate venv
source .venv/bin/activate

set -e

# install our package
uv pip install -e .[dev]

# let make know that we are installed in user mode
echo "Installed in dev mode"
touch .venv/.installed-dev
rm .venv/.installed || true
