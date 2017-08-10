#!/bin/bash

# download new files
python updater.py

# extract them
echo "extracting the files..."
gunzip protein.gbk.gz

echo "task completed..."

