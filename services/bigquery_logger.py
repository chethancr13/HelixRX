import json
from datetime import datetime, timezone


class BigQueryLogger:
    """Writes HelixRx analysis metadata to BigQuery."""

    def __init__(self, project_id=None, dataset_id="helixrx_analytics", table_id="analysis_metadata", auto_create=False):
        from google.cloud import bigquery

        self.bigquery = bigquery
        self.client = bigquery.Client(project=project_id)
        self.project_id = self.client.project
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.full_table_id = f"{self.project_id}.{self.dataset_id}.{self.table_id}"

        if auto_create:
            self._ensure_dataset_and_table()

    def _ensure_dataset_and_table(self):
        dataset_ref = self.bigquery.DatasetReference(self.project_id, self.dataset_id)
        table_ref = self.bigquery.TableReference(dataset_ref, self.table_id)

        try:
            self.client.get_dataset(dataset_ref)
        except Exception:
            dataset = self.bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            try:
                self.client.create_dataset(dataset)
            except Exception as e:
                if "Already Exists" not in str(e):
                    raise

        try:
            self.client.get_table(table_ref)
            return
        except Exception:
            pass

        schema = [
            self.bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            self.bigquery.SchemaField("logged_at", "TIMESTAMP", mode="REQUIRED"),
            self.bigquery.SchemaField("request_id", "STRING"),
            self.bigquery.SchemaField("endpoint", "STRING"),
            self.bigquery.SchemaField("status", "STRING"),
            self.bigquery.SchemaField("http_status", "INT64"),
            self.bigquery.SchemaField("error_message", "STRING"),
            self.bigquery.SchemaField("duration_ms", "INT64"),
            self.bigquery.SchemaField("client_ip", "STRING"),
            self.bigquery.SchemaField("user_agent", "STRING"),
            self.bigquery.SchemaField("patient_id", "STRING"),
            self.bigquery.SchemaField("drugs", "STRING"),
            self.bigquery.SchemaField("analysis_count", "INT64"),
            self.bigquery.SchemaField("llm_enabled", "BOOL"),
            self.bigquery.SchemaField("llm_provider", "STRING"),
            self.bigquery.SchemaField("request_metadata_json", "STRING"),
            self.bigquery.SchemaField("response_metadata_json", "STRING"),
        ]

        table = self.bigquery.Table(table_ref, schema=schema)
        try:
            self.client.create_table(table)
        except Exception as e:
            if "Already Exists" not in str(e):
                raise

    def log_analysis_event(self, payload: dict):
        row = {
            "event_id": payload.get("event_id"),
            "logged_at": payload.get("logged_at") or datetime.now(timezone.utc).isoformat(),
            "request_id": payload.get("request_id"),
            "endpoint": payload.get("endpoint", "/api/analysis"),
            "status": payload.get("status"),
            "http_status": payload.get("http_status"),
            "error_message": payload.get("error_message"),
            "duration_ms": payload.get("duration_ms"),
            "client_ip": payload.get("client_ip"),
            "user_agent": payload.get("user_agent"),
            "patient_id": payload.get("patient_id"),
            "drugs": payload.get("drugs"),
            "analysis_count": payload.get("analysis_count"),
            "llm_enabled": payload.get("llm_enabled", False),
            "llm_provider": payload.get("llm_provider", "gemini"),
            "request_metadata_json": self._to_json_string(payload.get("request_metadata")),
            "response_metadata_json": self._to_json_string(payload.get("response_metadata")),
        }

        errors = self.client.insert_rows_json(self.full_table_id, [row])
        if errors:
            raise RuntimeError(f"BigQuery insert failed: {errors}")

    @staticmethod
    def _to_json_string(value):
        if value is None:
            return None
        try:
            return json.dumps(value, ensure_ascii=True)
        except Exception:
            return json.dumps({"serialization_error": True}, ensure_ascii=True)
