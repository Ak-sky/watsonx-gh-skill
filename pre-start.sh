#!/bin/bash

# Tagging and running the image locally
nerdctl build --platform linux/amd64  -t gitskill .

nerdctl run -d --platform linux/amd64 -p 8000:8000 -e ACCESS_TOKEN=$ACCESS_TOKEN gitskill