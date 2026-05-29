from __future__ import annotations
from app.mock_data import REGIONS, BUSINESS_TYPES, REGION_SCORE_PRESETS, ANALYSIS_STORE, now_iso, expires_iso


def get_region(region_id: str):
    for region in REGIONS:
        if region["region_id"] == region_id:
            return region
    return None


def get_business_type(business_type_id: str):
    for bt in BUSINESS_TYPES:
        if bt["business_type_id"] == business_type_id:
            return bt
    return None


def make_analysis_id(region_id: str, business_type_id: str) -> str:
    return f"ANL-{business_type_id}-{region_id}"


def analyze(business_type_id: str, region_id: str, include_redzone_summary: bool = True):
    region = get_region(region_id)
    business_type = get_business_type(business_type_id)
    if not region:
        raise ValueError("REGION_NOT_FOUND")
    if not business_type:
        raise ValueError("BUSINESS_TYPE_NOT_FOUND")

    preset = REGION_SCORE_PRESETS.get(region_id, REGION_SCORE_PRESETS["GG-SUWON-YEONGTONG"])
    analysis_id = make_analysis_id(region_id, business_type_id)
    data = {
        "analysis_id": analysis_id,
        "business_type": {
            "business_type_id": business_type["business_type_id"],
            "name": business_type["name"],
        },
        "region": region,
        "score_summary": {
            "total_score": preset["total_score"],
            "decision": preset["decision"],
            "decision_code": preset["decision_code"],
            "survival_probability": preset["total_score"],
        },
        "scores": {
            "floating_population": preset["floating_population"],
            "competition": preset["competition"],
            "repeat_closure": preset["repeat_closure"],
            "rent_burden": preset["rent_burden"],
            "accessibility": preset["accessibility"],
        },
        "risk_labels": [
            {
                "label": "반복 폐업 위험" if preset["repeat_closure"] >= 70 else "반복 폐업 보통",
                "level": preset["risk_level"],
                "description": "최근 동일 업종의 반복 폐업 이력이 높게 나타났습니다." if preset["repeat_closure"] >= 70 else "동일 업종 반복 폐업 이력이 평균 수준입니다.",
            },
            {
                "label": "경쟁 과밀" if preset["competition"] >= 70 else "경쟁도 보통",
                "level": "HIGH" if preset["competition"] >= 80 else "MEDIUM",
                "description": "반경 300m 내 동일 업종 점포가 다수 존재합니다." if preset["competition"] >= 70 else "동일 업종 경쟁도는 관리 가능한 수준입니다.",
            },
        ],
        "key_metrics": {
            "daily_floating_population": preset["daily_floating_population"],
            "age_20_ratio": preset["age_20_ratio"],
            "store_count_same_category": preset["store_count_same_category"],
            "closure_rate_3y": preset["closure_rate_3y"],
            "short_term_closure_ratio": preset["short_term_closure_ratio"],
        },
        "redzone_summary": {
            "repeat_closure_score": preset["repeat_closure"],
            "risk_level": preset["risk_level"],
            "top_label": preset["label"],
            "closed_store_count": preset["store_count_same_category"],
            "short_term_closure_ratio": preset["short_term_closure_ratio"],
            "same_category_reclosure_ratio": preset["same_category_reclosure_ratio"],
            "same_location_reclosure_ratio": preset["same_location_reclosure_ratio"],
            "heatmap_available": True,
            "warning_marker_count": 5 if preset["risk_level"] == "HIGH" else 2,
        } if include_redzone_summary else None,
        "map": {
            "center": {"latitude": region["latitude"], "longitude": region["longitude"]},
            "zoom": 13,
        },
        "created_at": now_iso(),
        "expires_at": expires_iso(),
    }
    ANALYSIS_STORE[analysis_id] = data
    return data


def get_analysis(analysis_id: str):
    if analysis_id in ANALYSIS_STORE:
        return ANALYSIS_STORE[analysis_id]
    parts = analysis_id.split("-")
    if len(parts) >= 4 and parts[0] == "ANL":
        business_type_id = parts[1]
        region_id = "-".join(parts[2:])
        try:
            return analyze(business_type_id, region_id)
        except ValueError:
            return None
    return None
