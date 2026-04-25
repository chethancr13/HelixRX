# Deploy HelixRx Backend Behind Firebase Hosting

This wires Firebase Hosting and Flask backend on the same domain.

## 1) Deploy Flask backend to Cloud Run

Use project from `.firebaserc` (`helixrx-bff6c`):

```bash
gcloud config set project helixrx-bff6c

gcloud run deploy helixrx-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

If you want LLM enabled later, set env vars after deployment:

```bash
gcloud run services update helixrx-api \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=YOUR_KEY
```

## 2) Deploy Firebase Hosting rewrites

`firebase.json` already includes rewrite rules for `/api/**` and `/generate-report` to service `helixrx-api` in `us-central1`.

Deploy hosting + storage:

```bash
firebase deploy --only hosting,storage
```

## 3) Verify on same domain

Open:

- `https://helixrx-bff6c.web.app`

Then upload a VCF and provide drugs (comma-separated). The UI will:

1. Upload file to Firebase Storage
2. Call `/api/analysis` on same domain (rewritten to Cloud Run)
3. Display JSON response in-page

## Notes

- Current Storage rules are in bootstrap mode for unauthenticated upload with 5MB + `.vcf` limit.
- Tighten rules after adding Firebase Auth.
