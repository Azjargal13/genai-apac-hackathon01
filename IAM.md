Add Service account for Firestore

# gcloud projects add-iam-policy-binding gen-ai-hackathon01 \
#   --member="serviceAccount:energy-task-sa@gen-ai-hackathon01.iam.gserviceaccount.com" \
#   --role="roles/datastore.user"

#   gcloud iam service-accounts keys create energy-task-sa-key.json \
#   --iam-account="energy-task-sa@gen-ai-hackathon01.iam.gserviceaccount.com"