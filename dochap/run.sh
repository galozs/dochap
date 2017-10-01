echo "Creating new database..."
echo "Updating ucsc tables..."
rm db/transcript_aliases.txt -f
rm db/transcript_data.txt -f
python ucsc_downloader.py
python updater.py
