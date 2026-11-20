"""
MLflow experiment tracking for RAG configuration experiments.
Run this script to log a configuration + evaluation result to MLflow.

Usage:
    python mlops/mlflow/track_experiment.py

MLflow UI:
    mlflow ui        # opens at http://localhost:5000
"""
import json
import mlflow
from pathlib import Path

MLFLOW_TRACKING_URI = "sqlite:///mlruns.db"   # local folder; swap to an MLflow server URI for team use
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("insurance-agent-rag")


def evaluate_config(config: dict) -> dict:
    """
    Placeholder evaluation function.
    Replace with your actual eval set (questions + expected answers).
    Returns metrics: avg_latency_ms, retrieval_hit_rate, answer_faithfulness.
    """
    return {
        "avg_latency_ms": 850,
        "retrieval_hit_rate": 0.91,
        "answer_faithfulness": 0.87,
        "error_rate": 0.02,
    }


def run_experiment(config_path: str = "configs/rag_v1.yaml"):
    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    with mlflow.start_run(run_name=f"rag_{config['version']}"):
        mlflow.log_param("version", config["version"])
        mlflow.log_param("retriever_model", config["retriever"]["model"])
        mlflow.log_param("top_k", config["retriever"]["top_k"])
        mlflow.log_param("llm_provider", config["llm"]["provider"])
        mlflow.log_param("llm_model", config["llm"]["model"])
        mlflow.log_param("temperature", config["llm"]["temperature"])
        mlflow.log_param("latency_budget_ms", config["production"]["latency_budget_ms"])

        mlflow.log_artifact(config_path, artifact_path="configs")

        metrics = evaluate_config(config)
        for k, v in metrics.items():
            mlflow.log_metric(k, v)

        print(f"Logged run for config {config['version']}")
        print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    run_experiment()
