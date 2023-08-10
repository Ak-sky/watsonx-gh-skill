#!/bin/bash

# Tagging and running the image
nerdctl build -t gitskill .
nerdctl run -d -p 8000:8000 gitskill

# nerdctl tag gitskill:1.0 us.icr.io/bravehearts/gitskill:1.0