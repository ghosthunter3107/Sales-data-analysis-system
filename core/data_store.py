import os
import pandas as pd
from pathlib import Path
from config import Config

# In-memory store for active session dataset
_ACTIVE_DATASET = {
    "raw_df": None,
    "cleaned_df": None,
    "filename": None,
    "validation_report": None,
    "cleaning_report": None,
    "source": None  # 'upload', 'sample', 'database'
}

def set_raw_dataset(df, filename="uploaded.csv", source="upload"):
    """Store newly loaded raw dataset."""
    _ACTIVE_DATASET["raw_df"] = df.copy()
    _ACTIVE_DATASET["cleaned_df"] = None
    _ACTIVE_DATASET["filename"] = filename
    _ACTIVE_DATASET["validation_report"] = None
    _ACTIVE_DATASET["cleaning_report"] = None
    _ACTIVE_DATASET["source"] = source

def set_cleaned_dataset(df, report=None):
    """Store cleaned dataset and its cleaning report."""
    _ACTIVE_DATASET["cleaned_df"] = df.copy()
    _ACTIVE_DATASET["cleaning_report"] = report

def set_validation_report(report):
    """Store audit/validation inspection report."""
    _ACTIVE_DATASET["validation_report"] = report

def get_active_dataset():
    """Retrieve currently active datasets and metadata."""
    return _ACTIVE_DATASET

def has_active_data():
    """Check if clean or raw dataset is loaded."""
    return (_ACTIVE_DATASET["cleaned_df"] is not None and not _ACTIVE_DATASET["cleaned_df"].empty) or \
           (_ACTIVE_DATASET["raw_df"] is not None and not _ACTIVE_DATASET["raw_df"].empty)

def get_working_df():
    """Return cleaned_df if available, else raw_df."""
    if _ACTIVE_DATASET["cleaned_df"] is not None and not _ACTIVE_DATASET["cleaned_df"].empty:
        return _ACTIVE_DATASET["cleaned_df"]
    return _ACTIVE_DATASET["raw_df"]

def reset_dataset():
    """Reset active data store."""
    _ACTIVE_DATASET["raw_df"] = None
    _ACTIVE_DATASET["cleaned_df"] = None
    _ACTIVE_DATASET["filename"] = None
    _ACTIVE_DATASET["validation_report"] = None
    _ACTIVE_DATASET["cleaning_report"] = None
    _ACTIVE_DATASET["source"] = None
