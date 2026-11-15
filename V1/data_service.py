from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "people.xlsx"


def load_people(path=DATA_PATH):
    """Load and validate the teaching dataset."""
    df = pd.read_excel(path, sheet_name="People")
    required = {
        "Person_ID", "Name", "Nickname", "DOB", "Place_of_Stay",
        "Relationship", "Relationship_Group", "Relationship_Detail"
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")

    df = df.copy()
    df["DOB"] = pd.to_datetime(df["DOB"], errors="coerce")
    if df["DOB"].isna().any():
        bad = df[df["DOB"].isna()]["Person_ID"].tolist()
        raise ValueError(f"Invalid DOB values for: {bad}")

    for col in ["Name", "Nickname", "Place_of_Stay", "Relationship",
                "Relationship_Group", "Relationship_Detail"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    return df
