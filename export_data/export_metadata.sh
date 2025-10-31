# #!/bin/bash

USER="xuebing"
DB="mgdb"
EXPORT_DIR="/media/data/tracy/SRA-Search/export_data/metadata_db"
CHUNK=1000000
MIN_ID=1
MAX_ID=193504859

# mkdir -p "$EXPORT_DIR"

# current_id=$MIN_ID
# part=1

# while [ $current_id -le $MAX_ID ]; do
#   last_id=$((current_id + CHUNK - 1))
#   if [ $last_id -gt $MAX_ID ]; then
#     last_id=$MAX_ID
#   fi
#   echo "Exporting id $current_id to $last_id (file part $part)..."
#   psql -U "$USER" -d "$DB" -c "\COPY (SELECT * FROM metadata WHERE id BETWEEN $current_id AND $last_id ORDER BY id) TO '${EXPORT_DIR}/metadata_chunk_${current_id}_${last_id}.dat'"
#   current_id=$((last_id + 1))
#   part=$((part + 1))
# done

# echo "Export complete."

# psql -U "$USER" -d "$DB" -c "\COPY (SELECT * FROM geo_info) TO 'geo_info_db/geo_info.dat'"
# psql -U "$USER" -d "$DB" -c "\COPY (SELECT * FROM study) TO 'study_db/study.dat'"
# psql -U "$USER" -d "$DB" -c "\COPY (SELECT * FROM study_abstract) TO 'study_abstract_db/study_abstract.dat'"
psql -U "$USER" -d "$DB" -c "\COPY (SELECT tax_id, parent_tax_id, rank, scientific_name, common_name, genbank_common_name, synonym, children_ids, library_index FROM taxonomy) TO 'taxonomy_db/taxonomy.dat'"

# pg_dump -U "$USER" -d "$DB" -t metadata --schema-only > metadata_db/metadata_schema.sql
# pg_dump -U "$USER" -d "$DB" -t geo_info --schema-only > geo_info_db/geo_info_schema.sql
# pg_dump -U "$USER" -d "$DB" -t study --schema-only > study_db/study_schema.sql
# pg_dump -U "$USER" -d "$DB" -t study_abstract --schema-only > study_abstract_db/study_abstract_schema.sql
# pg_dump -U "$USER" -d "$DB" -t taxonomy --schema-only > taxonomy_db/taxonomy_schema.sql