#!/bin/bash
gcloud beta deployment-manager type-providers update folders --descriptor-url=https://folder-svc-pwh3e5n4pq-uc.a.run.app/openapi.json --api-options-file=api-options.yaml
