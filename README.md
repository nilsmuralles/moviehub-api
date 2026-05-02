# Maps Query — Cloud Function en Python

## Prueba local

```bash
pip install functions-framework
functions-framework --target=maps_query --port=8080
curl "http://localhost:8080?place=Torre+del+Reformador+Guatemala"
```

## Deploy a GCP

```bash
gcloud functions deploy maps-query \
  --gen2 --runtime=python312 --region=us-central1 \
  --source=. --entry-point=maps_query \
  --trigger-http --set-env-vars MAPS_KEY=TU_KEY
```

## Uso

```bash
curl "https://<REGION>-<PROJECT_ID>.cloudfunctions.net/maps-query?place=Mercado+Central+Guatemala"
```
