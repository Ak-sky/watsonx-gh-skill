#!/bin/bash

# Tagging and running the image
nerdctl build -t gitskill .
nerdctl run -d --platform linux/amd64 -p 8000:8000 -e ACCESS_TOKEN=$ACCESS_TOKEN gitskill


# nerdctl tag gitskill  icr.io/bravehearts/gitskill:2.0
# nerdctl push icr.io/bravehearts/gitskill