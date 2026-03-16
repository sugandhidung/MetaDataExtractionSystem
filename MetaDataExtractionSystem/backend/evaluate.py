"""
Evaluation module — computes per-field recall and generates predictions.
Compares extracted metadata against ground truth from CSV files.
"""

import csv
import logging
from pathlib import Path
from typing import Optional

from config import TRAIN_CSV, TEST_CSV, TRAIN_DIR, TEST_DIR
from models import EvaluationResult, EvaluationResponse, ExtractionResult
from extractor import process_document

logger = logging.getLogger(__name__)

# Mapping: CSV column → ExtractionResult field
FIELD_MAPPING = {
    "Aggrement Value": "agreement_value",
    "Aggrement Start Date": "agreement_start_date",
    "Aggrement End Date": "agreement_end_date",
    "Renewal Notice (Days)": "renewal_notice_days",
    "Party One": "party_one",
    "Party Two": "party_two",
}


def normalize_value(value: Optional[str]) -> str:
    """Normalize a value for comparison."""
    if value is None:
        return ""
    value = str(value).strip()
    value = " ".join(value.split())
    return value.lower()


def values_match(ground_truth: str, predicted: str) -> bool:
    """Check if two values match (flexible comparison)."""
    gt = normalize_value(ground_truth)
    pred = normalize_value(predicted)

    if not gt and not pred:
        return True
    if not gt or not pred:
        return False

    if gt == pred:
        return True

    # Numeric comparison
    try:
        gt_num = float(gt.replace(",", ""))
        pred_num = float(pred.replace(",", ""))
        if gt_num == pred_num:
            return True
    except ValueError:
        pass

    # Date separator normalization
    gt_date = gt.replace("/", ".").replace("-", ".")
    pred_date = pred.replace("/", ".").replace("-", ".")
    if gt_date == pred_date:
        return True

    # Substring match for party names with minor variations
    if gt in pred or pred in gt:
        return True

    return False


def load_ground_truth(csv_path: Path) -> dict:
    """Load ground truth from a CSV file."""
    ground_truth = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row["File Name"].strip()
            ground_truth[filename] = {
                csv_col: row.get(csv_col, "").strip()
                for csv_col in FIELD_MAPPING.keys()
            }
    return ground_truth


def find_file_in_directory(directory: Path, base_name: str) -> Optional[Path]:
    """Find a file in a directory matching the base name (any extension)."""
    for ext in [".docx", ".png", ".jpg", ".jpeg", ".pdf", ".pdf.docx"]:
        candidate = directory / f"{base_name}{ext}"
        if candidate.exists():
            return candidate
    # Glob fallback
    matches = list(directory.glob(f"{base_name}*"))
    if matches:
        return matches[0]
    return None


def _get_dirs(folder: str):
    if folder == "train":
        return TRAIN_CSV, TRAIN_DIR
    return TEST_CSV, TEST_DIR


def evaluate_on_dataset(folder: str = "train") -> EvaluationResponse:
    """Run extraction on a dataset and compute per-field recall."""
    csv_path, data_dir = _get_dirs(folder)
    ground_truth = load_ground_truth(csv_path)

    field_results = {field: {"true": 0, "false": 0} for field in FIELD_MAPPING}
    details = []

    for file_base_name, gt_values in ground_truth.items():
        file_path = find_file_in_directory(data_dir, file_base_name)

        if file_path is None:
            logger.warning(f"File not found for: {file_base_name}")
            for field in FIELD_MAPPING:
                field_results[field]["false"] += 1
            details.append({
                "filename": file_base_name,
                "status": "file_not_found",
                "matches": {},
            })
            continue

        result = process_document(file_path)
        extracted = result.metadata

        if result.status == "error":
            for field in FIELD_MAPPING:
                field_results[field]["false"] += 1
            details.append({
                "filename": file_base_name,
                "status": f"error: {result.error_message}",
                "matches": {},
            })
            continue

        file_matches = {}
        extracted_dict = extracted.model_dump()

        for csv_col, model_field in FIELD_MAPPING.items():
            gt_val = gt_values.get(csv_col, "")
            pred_val = extracted_dict.get(model_field)

            matched = values_match(gt_val, pred_val)
            if matched:
                field_results[csv_col]["true"] += 1
            else:
                field_results[csv_col]["false"] += 1

            file_matches[csv_col] = {
                "ground_truth": gt_val,
                "predicted": pred_val,
                "match": matched,
            }

        details.append({
            "filename": file_base_name,
            "status": "processed",
            "matches": file_matches,
        })

    per_field_recall = []
    total_true = total_false = 0

    for field, counts in field_results.items():
        t, f = counts["true"], counts["false"]
        total = t + f
        recall = t / total if total > 0 else 0.0
        per_field_recall.append(
            EvaluationResult(
                field=field, true_count=t, false_count=f,
                total=total, recall=round(recall, 4),
            )
        )
        total_true += t
        total_false += f

    overall = total_true / (total_true + total_false) if (total_true + total_false) > 0 else 0.0

    return EvaluationResponse(
        per_field_recall=per_field_recall,
        overall_recall=round(overall, 4),
        details=details,
    )


def generate_predictions(folder: str = "test") -> list[dict]:
    """Generate predictions for all files in a folder."""
    csv_path, data_dir = _get_dirs(folder)
    ground_truth = load_ground_truth(csv_path)
    predictions = []

    for file_base_name in ground_truth.keys():
        file_path = find_file_in_directory(data_dir, file_base_name)
        row = {
            "File Name": file_base_name,
            "Aggrement Value": "",
            "Aggrement Start Date": "",
            "Aggrement End Date": "",
            "Renewal Notice (Days)": "",
            "Party One": "",
            "Party Two": "",
            "_error": "",
        }

        if file_path is None:
            row["_error"] = f"File not found in {data_dir}"
            predictions.append(row)
            continue

        result = process_document(file_path)

        if result.status == "error":
            row["_error"] = result.error_message or "Unknown extraction error"
        else:
            ext = result.metadata
            row["Aggrement Value"] = ext.agreement_value or ""
            row["Aggrement Start Date"] = ext.agreement_start_date or ""
            row["Aggrement End Date"] = ext.agreement_end_date or ""
            row["Renewal Notice (Days)"] = ext.renewal_notice_days or ""
            row["Party One"] = ext.party_one or ""
            row["Party Two"] = ext.party_two or ""

        predictions.append(row)

    return predictions
