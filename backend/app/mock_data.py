from datetime import datetime, timedelta

BUSINESS_TYPES = [
    {
        "business_type_id": "CAFE",
        "name": "카페",
        "description": "커피전문점, 디저트카페, 휴게음식점 일부 포함",
        "icon": "coffee",
        "enabled": True,
    },
    {
        "business_type_id": "BUNSIK",
        "name": "분식",
        "description": "김밥, 떡볶이, 간편식 중심 업종",
        "icon": "bowl",
        "enabled": True,
    },
    {
        "business_type_id": "BEAUTY_SALON",
        "name": "미용실",
        "description": "미용업, 헤어샵 중심 업종",
        "icon": "scissors",
        "enabled": True,
    },
]

REGIONS = [
    {
        "region_id": "GG-SUWON-YEONGTONG",
        "sido": "경기도",
        "sigungu": "수원시 영통구",
        "dong": "광교1동",
        "display_name": "경기도 수원시 영통구 광교1동",
        "latitude": 37.2911,
        "longitude": 127.0465,
        "available": True,
    },
    {
        "region_id": "GG-SUWON-GWONSEON",
        "sido": "경기도",
        "sigungu": "수원시 권선구",
        "dong": "권선동",
        "display_name": "경기도 수원시 권선구 권선동",
        "latitude": 37.2573,
        "longitude": 127.0297,
        "available": True,
    },
    {
        "region_id": "GG-SEONGNAM-BUNDANG",
        "sido": "경기도",
        "sigungu": "성남시 분당구",
        "dong": "정자동",
        "display_name": "경기도 성남시 분당구 정자동",
        "latitude": 37.3596,
        "longitude": 127.1054,
        "available": True,
    },
]

ANALYSIS_STORE = {}
REPORT_STORE = {}

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def expires_iso():
    return (datetime.now() + timedelta(days=90)).isoformat(timespec="seconds")

REGION_SCORE_PRESETS = {
    "GG-SUWON-YEONGTONG": {
        "total_score": 64,
        "decision": "조건부 검토",
        "decision_code": "NORMAL",
        "floating_population": 76,
        "competition": 58,
        "repeat_closure": 78,
        "rent_burden": None,
        "accessibility": 81,
        "daily_floating_population": 82451,
        "age_20_ratio": 28.7,
        "store_count_same_category": 36,
        "closure_rate_3y": 8.6,
        "short_term_closure_ratio": 42.0,
        "risk_level": "HIGH",
        "label": "카페 반복 폐업 위험 지역",
        "same_category_reclosure_ratio": 68.0,
        "same_location_reclosure_ratio": 54.0,
    },
    "GG-SUWON-GWONSEON": {
        "total_score": 76,
        "decision": "창업 적합",
        "decision_code": "GOOD",
        "floating_population": 71,
        "competition": 62,
        "repeat_closure": 52,
        "rent_burden": None,
        "accessibility": 70,
        "daily_floating_population": 61120,
        "age_20_ratio": 22.4,
        "store_count_same_category": 21,
        "closure_rate_3y": 5.2,
        "short_term_closure_ratio": 24.0,
        "risk_level": "MEDIUM",
        "label": "반복 폐업 보통 지역",
        "same_category_reclosure_ratio": 35.0,
        "same_location_reclosure_ratio": 22.0,
    },
    "GG-SEONGNAM-BUNDANG": {
        "total_score": 48,
        "decision": "주의 필요",
        "decision_code": "CAUTION",
        "floating_population": 82,
        "competition": 85,
        "repeat_closure": 76,
        "rent_burden": None,
        "accessibility": 70,
        "daily_floating_population": 98200,
        "age_20_ratio": 19.8,
        "store_count_same_category": 58,
        "closure_rate_3y": 11.4,
        "short_term_closure_ratio": 39.0,
        "risk_level": "HIGH",
        "label": "경쟁 과밀형 위험 상권",
        "same_category_reclosure_ratio": 72.0,
        "same_location_reclosure_ratio": 47.0,
    },
}
