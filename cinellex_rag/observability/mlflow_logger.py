import mlflow
import time
from functools import wraps


mlflow.set_experiment("cinellex-ai")


def start_run(query: str, route: str):
    mlflow.start_run()
    mlflow.log_param("query", query)
    mlflow.log_param("route", route)
    return time.time()


def log_latency(start_time: float, key: str):
    latency = time.time() - start_time
    mlflow.log_metric(key, latency)
    return latency


def log_output(output: str):
    mlflow.log_param("output", output)


def end_run():
    mlflow.end_run()

def log_run(query: str, route: str, response):
    with mlflow.start_run():
        mlflow.log_param("query", query)
        mlflow.log_param("route", route)

        mlflow.log_text(str(response), "response.txt")