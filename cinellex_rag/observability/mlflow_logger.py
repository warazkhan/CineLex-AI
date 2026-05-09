import mlflow
import time

mlflow.set_experiment("cinellex-ai")


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
        pass  # collected at end

    def log_latency(self, step: str):
        pass  # collected at end

    def log_response(self, response: dict):
        # extract source from response metadata
        if isinstance(response, dict):
            self._source = response.get("metadata", {}).get("source", "unknown")

    def end_run(self):
        with mlflow.start_run():
            # params
            mlflow.log_param("query", self._query or "")
            mlflow.log_param("route", self._route or "")
            mlflow.log_param("source", self._source or "unknown")

            # metrics — now visible in Metrics tab
            latency = round((time.time() - self._start_time) * 1000)
            mlflow.log_metric("latency_ms", latency)


# singleton
logger = MLflowLogger()