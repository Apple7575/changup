"""
반복 폐업 지수 샘플 계산 스크립트.

사용법:
  python scripts/calc_repeat_closure.py --input data/sample_closure_data.csv --output data/repeat_closure_result.csv

필수 컬럼 예시:
  business_name, business_type_id, status, opened_at, closed_at, address_clean, latitude, longitude, geocode_status

실제 행정안전부 인허가 CSV를 쓰는 경우 컬럼명을 아래 표준 컬럼명으로 먼저 맞추면 됩니다.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import pandas as pd


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def greedy_cluster(df: pd.DataFrame, radius_m: float = 100.0) -> pd.DataFrame:
    rows = df.reset_index(drop=True).copy()
    rows["cluster_id"] = None
    cluster_idx = 1
    for i, row in rows.iterrows():
        if pd.notna(rows.at[i, "cluster_id"]):
            continue
        cid = f"CLU-{cluster_idx:04d}"
        rows.at[i, "cluster_id"] = cid
        for j in range(i + 1, len(rows)):
            if pd.notna(rows.at[j, "cluster_id"]):
                continue
            if rows.at[j, "business_type_id"] != row["business_type_id"]:
                continue
            dist = haversine_m(row["latitude"], row["longitude"], rows.at[j, "latitude"], rows.at[j, "longitude"])
            if dist <= radius_m:
                rows.at[j, "cluster_id"] = cid
        cluster_idx += 1
    return rows


def calculate(input_path: Path, output_path: Path, radius_m: float = 100.0):
    df = pd.read_csv(input_path)
    required = {"business_type_id", "status", "opened_at", "closed_at", "latitude", "longitude", "geocode_status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
    df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")
    target = df[
        (df["status"] == "CLOSED")
        & (df["geocode_status"] == "SUCCESS")
        & df["latitude"].notna()
        & df["longitude"].notna()
        & df["business_type_id"].notna()
    ].copy()
    target["operation_months"] = ((target["closed_at"] - target["opened_at"]).dt.days / 30.44).round(1)
    target["is_short_term_closed"] = target["operation_months"].le(24)

    clustered = greedy_cluster(target, radius_m=radius_m)
    summary = clustered.groupby(["cluster_id", "business_type_id"]).agg(
        center_latitude=("latitude", "mean"),
        center_longitude=("longitude", "mean"),
        closure_count=("status", "count"),
        short_term_closure_count=("is_short_term_closed", "sum"),
    ).reset_index()
    summary["short_term_closure_ratio"] = (summary["short_term_closure_count"] / summary["closure_count"] * 100).round(1)
    # MVP용 반복 폐업 점수: 폐업 건수와 단기 폐업 비율을 조합한 단순 점수.
    summary["repeat_closure_score"] = (
        (summary["closure_count"].clip(upper=10) / 10 * 50)
        + (summary["short_term_closure_ratio"] / 100 * 50)
    ).round().astype(int)
    summary["risk_level"] = pd.cut(
        summary["repeat_closure_score"],
        bins=[-1, 39, 69, 100],
        labels=["LOW", "MEDIUM", "HIGH"],
    ).astype(str)
    summary["pattern_label"] = summary.apply(lambda r: f"{r['business_type_id']} 반복 폐업 위험 지역" if r["risk_level"] == "HIGH" else f"{r['business_type_id']} 반복 폐업 관찰 지역", axis=1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(summary)} clusters to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--radius", type=float, default=100.0)
    args = parser.parse_args()
    calculate(Path(args.input), Path(args.output), args.radius)
