#!/bin/bash
# move new read me to old readme
mv db/readme_new db/readme_old
# extract them
echo "extracting the files..."
gunzip db/protein.gbk.gz -f
echo "Parsing protein.gbk..."
python gbk_parser.py
echo "Removing some symbols..."
# when making this tool for windows, remember to find replacement for this, probably in python.
sed -i "s/'//g" aliases.txt
echo "Deleting old database..."
rm db/aliases.db -f
echo "Creating Aliases database..."
python db_creator.py
echo "setup complete."

