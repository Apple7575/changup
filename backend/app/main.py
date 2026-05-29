from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.models import AnalyzeRequest, ReportRequest, ChatRequest, CompareRequest
from app.mock_data import BUSINESS_TYPES, REGIONS
from app.services.analysis_service import analyze, get_analysis
from app.services.redzone_service import get_redzones
from app.services.report_service import generate_report, answer_question

load_dotenv()

app = FastAPI(title="창업나침반 경기 API", version="1.1.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ok(data, message="요청이 성공적으로 처리되었습니다."):
    return {"success": True, "data": data, "message": message}


@app.get("/api/health")
def health():
    return ok({"status": "ok", "service": "changup-nachimban-api", "version": "1.1.0"}, "서버가 정상 작동 중입니다.")


@app.get("/api/business-types")
def business_types():
    return ok({"business_types": BUSINESS_TYPES}, "분석 가능 업종 목록을 조회했습니다.")


@app.get("/api/regions")
def regions(sido: str | None = None, sigungu: str | None = None, available_only: bool = True):
    result = REGIONS
    if sido:
        result = [r for r in result if r["sido"] == sido]
    if sigungu:
        result = [r for r in result if r["sigungu"] == sigungu]
    if available_only:
        result = [r for r in result if r.get("available", True)]
    return ok({"regions": result}, "분석 가능 지역 목록을 조회했습니다.")


@app.post("/api/analyze")
def analyze_endpoint(req: AnalyzeRequest):
    try:
        data = analyze(req.business_type_id, req.region_id, req.include_redzone_summary)
        return ok(data, "상권 분석이 완료되었습니다.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/analysis/{analysis_id}")
def analysis_endpoint(analysis_id: str):
    data = get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="ANALYSIS_DATA_NOT_FOUND")
    return ok(data, "분석 결과를 조회했습니다.")


@app.get("/api/redzones")
def redzones_endpoint(
    business_type_id: str,
    region_id: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius: int | None = Query(2000),
    sw_lat: float | None = None,
    sw_lng: float | None = None,
    ne_lat: float | None = None,
    ne_lng: float | None = None,
    risk_level: str | None = None,
):
    data = get_redzones(business_type_id, region_id, lat, lng, radius)
    if risk_level:
        data["warning_markers"] = [m for m in data["warning_markers"] if m["risk_level"] == risk_level]
    data["bbox"] = {"sw_lat": sw_lat, "sw_lng": sw_lng, "ne_lat": ne_lat, "ne_lng": ne_lng}
    return ok(data, "반복 폐업 레드존 상세 데이터를 조회했습니다.")


@app.post("/api/report")
def report_endpoint(req: ReportRequest):
    data = generate_report(req.model_dump())
    return ok(data, "AI 상권 생존 리포트가 생성되었습니다.")


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    data = answer_question(req.model_dump())
    return ok(data, "추가 질의응답이 생성되었습니다.")


@app.post("/api/compare")
def compare_endpoint(req: CompareRequest):
    comparison = []
    analysis_items = []
    if req.analysis_ids:
        for aid in req.analysis_ids:
            item = get_analysis(aid)
            if item:
                analysis_items.append(item)
    if not analysis_items and req.region_ids:
        for rid in req.region_ids:
            analysis_items.append(analyze(req.business_type_id, rid))
    if not analysis_items:
        raise HTTPException(status_code=400, detail="INVALID_REQUEST")

    sorted_items = sorted(analysis_items, key=lambda x: x["score_summary"]["total_score"], reverse=True)
    for idx, item in enumerate(sorted_items, start=1):
        score = item["score_summary"]["total_score"]
        recommendation = "추천" if score >= 75 else "조건부 추천" if score >= 60 else "비추천"
        comparison.append({
            "analysis_id": item["analysis_id"],
            "region_id": item["region"]["region_id"],
            "display_name": item["region"]["sigungu"],
            "rank": idx,
            "recommendation": recommendation,
            "scores": {
                "total_score": score,
                "repeat_closure": item["scores"]["repeat_closure"],
                "competition": item["scores"]["competition"],
                "rent_burden": item["scores"].get("rent_burden"),
                "accessibility": item["scores"]["accessibility"],
            },
            "ai_summary": "반복 폐업 위험과 접근성을 함께 고려한 비교 결과입니다.",
        })
    return ok({
        "business_type": {"business_type_id": req.business_type_id, "name": "카페"},
        "comparison": comparison,
        "best_region_id": comparison[0]["region_id"],
        "used_cache": bool(req.analysis_ids or req.use_cache),
    }, "후보 입지 비교가 완료되었습니다.")
