#!/bin/bash
# move new read me to old readme
mv db/readme_new db/readme_old
# extract them
echo "Extracting the files..."
gunzip db/protein.gbk.gz -f
echo "Updating ucsc tables..."
rm db/transcript_aliases.txt -f
rm db/transcript_data.txt -f
python ucsc_downloader.py
echo "Deleting old database..."
rm db/aliases.db -f
rm db/comb.db -f
python db_creator.py
#rm db/protein.gbk -f
echo "assigning domains to exons..."
# add column to db

echo "Setup complete."

