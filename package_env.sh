#!/bin/bash
# Download all required wheels for offline installation.
set -e
mkdir -p wheels
pip download -r requirements.txt -d wheels
