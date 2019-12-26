#!/bin/bash
FOLDER_NAME=$1
ORGANIZATION_ID=$2

FOLDER_ID=$(gcloud alpha resource-manager folders list --organization $ORGANIZATION_ID
76 --format="csv(display_name, ID)" | grep $FOLDER_NAME | cut -d "," -f2)    

echo $FOLDER_ID