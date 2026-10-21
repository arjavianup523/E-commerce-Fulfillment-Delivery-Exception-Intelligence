
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "fulfillment.db"
SQL_PATH = ROOT / "sql" / "analysis_queries.sql"
OUTPUT_DIR = ROOT / "reports" / "sql_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sql_text = SQL_PATH.read_text(encoding="utf-8")
queries = [
    query.strip()
    for query in sql_text.split(";")
    if query.strip() and query.strip().startswith("--") is False
]

# Remove leading SQL comments from each query.
clean_queries = []
for query in sql_text.split(";"):
    lines = [
        line for line in query.splitlines()
        if line.strip() and not line.strip().startswith("--")
    ]
    cleaned = "\n".join(lines).strip()
    if cleaned:
        clean_queries.append(cleaned)

with sqlite3.connect(DB_PATH) as connection:
    for index, query in enumerate(clean_queries, start=1):
        result = pd.read_sql_query(query, connection)

        output_path = OUTPUT_DIR / f"query_{index}.csv"
        result.to_csv(output_path, index=False)

        print(f"\n--- Query {index} ---")
        print(result.to_string(index=False))
        print(f"Saved: {output_path}")

print("\nSQL analysis completed.")
