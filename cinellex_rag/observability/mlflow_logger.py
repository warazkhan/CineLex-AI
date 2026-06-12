"""MLflow run logger.

On free-tier Render the default local ``./mlruns`` store is wiped on every
spin-down (and there is no MLflow UI server to read it), so logging there is
pure overhead. We therefore only log when an explicit ``MLFLOW_TRACKING_URI`` is
configured — a remote/managed tracking server, or a local one in dev. When it is
unset every method is a no-op and ``mlflow`` is never imported, so the
(skinny) dependency adds no startup cost or memory in production.
"""
import os
import time

_ENABLED = bool(os.environ.get("MLFLOW_TRACKING_URI"))

if _ENABLED:
    import mlflow

    mlflow.set_experiment(os.environ.get("MLFLOW_EXPERIMENT", "cinellex-ai"))


class MLflowLogger:
    def __init__(self):
        self._query = None
        self._route = None
        self._source = None
        self._start_time = None

    def start_run(self, query: str):
        self._query = query
        self._start_time = time.time()

    def log_route(self, route: str):
        self._route = route

    def log_node(self, node: str, metadata: dict = None):
        pass  # node-level detail is summarised into the single end-of-run record

    def log_response(self, response: dict):
        # extract source from response metadata
        if isinstance(response, dict):
            self._source = response.get("metadata", {}).get("source", "unknown")

    def end_run(self):
        if not _ENABLED:
            return

        with mlflow.start_run():
            # params
            mlflow.log_param("query", self._query or "")
            mlflow.log_param("route", self._route or "")
            mlflow.log_param("source", self._source or "unknown")

            # metrics — now visible in Metrics tab
            latency = round((time.time() - (self._start_time or time.time())) * 1000)
            mlflow.log_metric("latency_ms", latency)


# singleton
logger = MLflowLogger()
