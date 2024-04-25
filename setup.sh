#!/bin/bash

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Execute commands from pythoncmd.txt
while read -r line; do
    python -c "$line"
done < pythoncmd.txt
