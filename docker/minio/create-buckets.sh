#!/bin/sh
# Create default buckets in MinIO after startup.
# Usage: docker exec minio sh /create-buckets.sh

mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb --ignore-existing local/openskill
echo "Bucket 'openskill' ready."
