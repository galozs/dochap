#!/bin/bash
# move new read me to old readme
mv db/readme_new db/readme_old
# extract them
echo "extracting the files..."
gunzip db/protein.gbk.gz -f
echo "Deleting old database..."
rm db/aliases.db -f
rm db/comb.db -f
python db_creator.py
rm db/protein.gbk -f
echo "setup complete."

