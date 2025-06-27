from sklearn.model_selection import cross_val_score
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import logging
import json
import os

from data.database import save_classification_pipeline

def evaluate_pipeline(pipeline, sentences: list[str], classifications: list[int]) -> float:
    """
    Calcula o score de acurácia de um modelo de classificação.
    """
    cv_results = cross_val_score(pipeline, sentences, classifications, cv=5, scoring='accuracy', error_score='raise', n_jobs=-1)
    score = cv_results.mean() - cv_results.std()
    return score

def compare_pipelines(pipelines, sentences: list[str], classifications: list[int]) -> list[float]:
    """
    Compara múltiplos pipelines de classificação e retorna os scores.
    """
    scores = []
    for id, pipeline in tqdm(pipelines.items(), desc="Avaliando pipelines..."):
        score = evaluate_pipeline(pipeline, sentences, classifications)
        scores.append((id, score))
        log_pipeline_evaluation(id, pipeline, score)
        save_classification_pipeline(id, pipeline, score)
    scores = sorted(scores, key=lambda item: item[1], reverse=True)
    return scores

def log_pipeline_evaluation(pipeline_id: str, pipeline, score: float, log_dir: str = "logs"):
    """
    Registra a avaliação do pipeline em um arquivo de log.
    """
    Path(log_dir).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_file = os.path.join(log_dir, "pipeline_evaluation.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )

    # Extração dos passos do pipeline
    named_steps = {name: str(step) for name, step in pipeline.named_steps.items()}

    log_entry = {
        "timestamp": timestamp,
        "pipeline_id": pipeline_id,
        "named_steps": named_steps,
        "score": round(score, 4)
    }

    logging.info(json.dumps(log_entry, ensure_ascii=False, indent=4))