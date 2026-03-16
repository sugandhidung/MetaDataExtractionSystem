"""
Script to generate predictions for the test set and evaluate on train set.
Usage:  python generate_predictions.py
"""

import csv
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(__file__))

from config import PREDICTIONS_DIR
from evaluate import generate_predictions, evaluate_on_dataset
from llm_extractor import get_provider_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def save_predictions_csv(predictions: list[dict], output_path: str):
    fieldnames = [
        "File Name", "Aggrement Value", "Aggrement Start Date",
        "Aggrement End Date", "Renewal Notice (Days)", "Party One", "Party Two",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(predictions)
    logger.info(f"Predictions saved to: {output_path}")


def main():
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)

    provider = get_provider_name()
    print(f"\n  LLM Provider: {provider or 'NONE — set OPENAI_API_KEY, GROQ_API_KEY, or run Ollama'}\n")

    if not provider:
        print("ERROR: No LLM provider available. Cannot generate predictions.")
        print("  Set one of: OPENAI_API_KEY, GROQ_API_KEY, or start Ollama.")
        sys.exit(1)

    # ── Train Set Evaluation ──
    print("=" * 60)
    print("EVALUATING ON TRAIN SET")
    print("=" * 60)

    train_eval = evaluate_on_dataset("train")
    print(f"\nOverall Recall: {train_eval.overall_recall:.2%}")
    print("\nPer-Field Recall:")
    print("-" * 50)
    for field in train_eval.per_field_recall:
        bar = "█" * int(field.recall * 20) + "░" * (20 - int(field.recall * 20))
        print(f"  {field.field:<30} {bar} {field.recall:.2%} ({field.true_count}/{field.total})")

    for detail in train_eval.details:
        print(f"\n  {detail['filename']} ({detail['status']})")
        for field_name, info in detail.get("matches", {}).items():
            icon = "✓" if info["match"] else "✗"
            print(f"    {icon} {field_name}: GT='{info['ground_truth']}' | Pred='{info['predicted']}'")

    # ── Test Set Predictions ──
    print("\n" + "=" * 60)
    print("GENERATING TEST SET PREDICTIONS")
    print("=" * 60)

    test_predictions = generate_predictions("test")
    output_path = PREDICTIONS_DIR / "test_predictions.csv"
    save_predictions_csv(test_predictions, str(output_path))

    for pred in test_predictions:
        print(f"\n  {pred['File Name']}")
        if pred.get("_error"):
            print(f"    ERROR: {pred['_error']}")
        else:
            print(f"    Value: {pred['Aggrement Value'] or 'N/A'}")
            print(f"    Start: {pred['Aggrement Start Date'] or 'N/A'}")
            print(f"    End:   {pred['Aggrement End Date'] or 'N/A'}")
            print(f"    Notice: {pred['Renewal Notice (Days)'] or 'N/A'}")
            print(f"    Party1: {pred['Party One'] or 'N/A'}")
            print(f"    Party2: {pred['Party Two'] or 'N/A'}")

    # ── Test Set Evaluation ──
    print("\n" + "-" * 40)
    print("TEST SET RECALL")
    print("-" * 40)
    test_eval = evaluate_on_dataset("test")
    print(f"\nOverall Recall: {test_eval.overall_recall:.2%}")
    for field in test_eval.per_field_recall:
        bar = "█" * int(field.recall * 20) + "░" * (20 - int(field.recall * 20))
        print(f"  {field.field:<30} {bar} {field.recall:.2%} ({field.true_count}/{field.total})")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
