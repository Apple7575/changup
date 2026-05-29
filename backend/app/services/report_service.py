from app.mock_data import REPORT_STORE, now_iso


def generate_report(payload: dict):
    analysis_id = payload.get("analysis_id")
    region = payload.get("region", {}).get("display_name", "선택 지역")
    business_name = payload.get("business_type", {}).get("name", "선택 업종")
    score = payload.get("score_summary", {}).get("total_score", 64)
    decision = payload.get("score_summary", {}).get("decision", "조건부 검토")
    scores = payload.get("scores", {})
    repeat_score = scores.get("repeat_closure", 78)
    competition_score = scores.get("competition", 58)
    report_id = f"RPT-{analysis_id}" if analysis_id else "RPT-DEMO"

    one_line = "유동인구와 접근성은 양호하지만 반복 폐업 패턴과 경쟁 과밀에 주의가 필요합니다."
    if score >= 75:
        one_line = "반복 폐업 위험이 낮고 접근성이 양호해 창업 검토 가치가 높은 지역입니다."
    elif score < 50:
        one_line = "반복 폐업과 경쟁 과밀 위험이 높아 대체 입지를 우선 검토해야 합니다."

    data = {
        "report_id": report_id,
        "analysis_id": analysis_id,
        "status": "COMPLETED",
        "title": f"{region} {business_name} 상권 생존 리포트",
        "summary": {"survival_score": score, "decision": decision, "one_line": one_line},
        "sections": [
            {"section_id": "survival", "title": "생존 가능성", "content": f"선택한 상권의 종합 점수는 {score}점이며, 판정은 '{decision}'입니다. 유동인구와 접근성은 긍정 요인이지만 위험 지표를 함께 확인해야 합니다."},
            {"section_id": "risks", "title": "주요 리스크", "content": f"반복 폐업 지수는 {repeat_score}점, 경쟁도는 {competition_score}점입니다. 동일 업종이 반복적으로 실패한 이력이 있는지 우선 확인해야 합니다."},
            {"section_id": "closure_pattern", "title": "폐업 패턴 분석", "content": "해당 지역은 카페 업종의 단기 폐업 비율과 동일 업종 재폐업 패턴을 함께 확인해야 하는 상권입니다. 겉보기 유동인구만으로 안전한 입지라고 판단하기 어렵습니다."},
            {"section_id": "strategy", "title": "추천 전략", "content": "일반 카페보다 테이크아웃 특화, 직장인 점심 수요, 회전율 중심 메뉴, 배달·포장 중심 운영 전략을 검토하는 것이 좋습니다."},
            {"section_id": "alternative", "title": "대체 입지", "content": "반복 폐업 지수가 낮고 접근성이 유지되는 수원시 권선구, 수원시 장안구를 비교 후보로 검토할 수 있습니다."},
        ],
        "disclaimer": "본 분석 결과는 공공데이터 기반 참고자료이며 실제 창업 성과를 보장하지 않습니다.",
        "created_at": now_iso(),
    }
    REPORT_STORE[report_id] = data
    return data


def answer_question(payload: dict):
    question = payload.get("question", "")
    snapshot = payload.get("analysis_snapshot") or {}
    scores = snapshot.get("scores", {})
    repeat_score = scores.get("repeat_closure", 78)
    competition_score = scores.get("competition", 58)
    if "20대" in question:
        answer = "20대 유동인구는 카페·분식 업종의 즉시 방문 수요를 판단하는 핵심 지표입니다. 다만 20대 비율이 높더라도 반복 폐업 지수가 높다면 가격대, 회전율, 테이크아웃 수요를 함께 검토해야 합니다."
    elif "프랜차이즈" in question:
        answer = "프랜차이즈는 초기 인지도와 운영 매뉴얼 측면에서 유리할 수 있습니다. 그러나 해당 지역의 반복 폐업 지수와 경쟁도가 높다면 브랜드 여부와 별개로 입지 자체의 위험은 여전히 검토해야 합니다."
    elif "대체" in question:
        answer = "대체 지역은 반복 폐업 지수가 낮고 접근성 또는 유동인구가 유지되는 지역을 우선 추천합니다. 현재 후보 중에서는 수원시 권선구가 상대적으로 안정적인 비교 대상입니다."
    else:
        answer = "해당 질문은 분석 결과의 반복 폐업 지수, 경쟁도, 접근성 지표를 기준으로 판단해야 합니다. 점수가 높은 위험 항목을 먼저 낮출 수 있는 운영 전략을 검토하는 것이 좋습니다."
    return {
        "answer_id": "CHAT-DEMO-0001",
        "question": question,
        "answer": answer,
        "evidence": [
            {"metric": "반복 폐업 지수", "value": repeat_score, "interpretation": "위험" if repeat_score >= 70 else "보통"},
            {"metric": "경쟁도", "value": competition_score, "interpretation": "위험" if competition_score >= 70 else "보통"},
        ],
        "created_at": now_iso(),
    }
