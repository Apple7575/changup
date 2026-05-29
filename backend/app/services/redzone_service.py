from app.services.analysis_service import get_region


def get_redzones(business_type_id: str, region_id: str | None = None, lat: float | None = None, lng: float | None = None, radius: int | None = 2000):
    center_lat = lat
    center_lng = lng
    if region_id:
        region = get_region(region_id)
        if region:
            center_lat = region["latitude"]
            center_lng = region["longitude"]
    center_lat = center_lat or 37.2911
    center_lng = center_lng or 127.0465

    heatmap_points = [
        {"latitude": center_lat + 0.0008, "longitude": center_lng + 0.0006, "weight": 0.87, "repeat_closure_score": 87},
        {"latitude": center_lat - 0.0010, "longitude": center_lng - 0.0009, "weight": 0.74, "repeat_closure_score": 74},
        {"latitude": center_lat + 0.0016, "longitude": center_lng - 0.0010, "weight": 0.68, "repeat_closure_score": 68},
        {"latitude": center_lat - 0.0014, "longitude": center_lng + 0.0012, "weight": 0.61, "repeat_closure_score": 61},
    ]
    warning_markers = [
        {
            "marker_id": "RZ-001",
            "cluster_id": "CLU-SUWON-CAFE-001",
            "latitude": center_lat + 0.0008,
            "longitude": center_lng + 0.0006,
            "title": "카페 반복 폐업 위험 지역",
            "risk_level": "HIGH",
            "repeat_closure_score": 87,
            "closed_store_count": 6,
            "short_term_closure_ratio": 61.0,
            "same_location_reclosure_ratio": 55.0,
            "same_category_reclosure_ratio": 72.0,
            "timeline": {"opened": 102, "closed": 61, "reopened": 34, "reclosed": 19, "reclosure_ratio": 55.9},
        },
        {
            "marker_id": "RZ-002",
            "cluster_id": "CLU-SUWON-CAFE-002",
            "latitude": center_lat - 0.0010,
            "longitude": center_lng - 0.0009,
            "title": "동일 업종 단기 폐업 주의",
            "risk_level": "MEDIUM",
            "repeat_closure_score": 74,
            "closed_store_count": 4,
            "short_term_closure_ratio": 45.0,
            "same_location_reclosure_ratio": 31.0,
            "same_category_reclosure_ratio": 52.0,
            "timeline": {"opened": 48, "closed": 22, "reopened": 10, "reclosed": 4, "reclosure_ratio": 40.0},
        },
    ]
    return {
        "business_type_id": business_type_id,
        "region_id": region_id,
        "query_area": {"lat": center_lat, "lng": center_lng, "radius": radius},
        "heatmap_points": heatmap_points,
        "warning_markers": warning_markers,
    }
