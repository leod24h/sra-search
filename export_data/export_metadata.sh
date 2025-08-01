#!/bin/bash

USER="xuebing"
DB="mgdb"
EXPORT_DIR="/media/data/tracy/SRA-Search/export_data/metadata_db"
CHUNK=1000000
MIN_ID=1
MAX_ID=193504859

mkdir -p "$EXPORT_DIR"

current_id=$MIN_ID
part=1

while [ $current_id -le $MAX_ID ]; do
  last_id=$((current_id + CHUNK - 1))
  if [ $last_id -gt $MAX_ID ]; then
    last_id=$MAX_ID
  fi
  echo "Exporting id $current_id to $last_id (file part $part)..."
  psql -U "$USER" -d "$DB" -c "\COPY (SELECT * FROM metadata WHERE id BETWEEN $current_id AND $last_id ORDER BY id) TO '${EXPORT_DIR}/metadata_chunk_${current_id}_${last_id}.dat'"
  current_id=$((last_id + 1))
  part=$((part + 1))
done

echo "Export complete."