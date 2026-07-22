import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from src.agent.pipeline.storing_results import _read_json
import json

ROOT = Path(__file__).resolve().parents[3]
STORE_FILE = ROOT / "data" / "raw" / "articles.json"
SENTIMENT_SCORE_FILE = ROOT / "data" / "sentiment_score" / "sentiment_score.json"
load_dotenv(ROOT / ".env")

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN introuvable. Vérifie que le fichier .env existe à la racine "
        "du projet et qu'il contient la ligne HF_TOKEN=..."
    )

client = InferenceClient(
    api_key=HF_TOKEN,
)
def get_sentiment(summary):
    result = client.text_classification(
        summary,
    model="ProsusAI/finbert",)
    return result
def article_sentiment_analysis(path:str):
    articles = _read_json(path)
    results = {}
    for article_id, article in articles.items():
        score = get_sentiment(article["summary"])
        results[article_id] = score
    with open(SENTIMENT_SCORE_FILE, "w") as f:
        json.dump(results, f, indent=4)


article_sentiment_analysis(STORE_FILE)

#result = client.text_classification(
 #   "The stock is getting much attention after last weeks up trend",
 #   model="ProsusAI/finbert",)

#print(result)