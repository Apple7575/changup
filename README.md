# 창업나침반 경기 MVP

공공데이터 기반 반복 폐업 패턴 분석을 통해 예비창업자의 창업 입지 위험을 진단하는 웹 MVP입니다.

## 포함된 것

- React + Vite 프론트엔드
- FastAPI 백엔드
- Mock API 7종
  - `/api/business-types`
  - `/api/regions`
  - `/api/analyze`
  - `/api/analysis/{analysis_id}`
  - `/api/redzones`
  - `/api/report`
  - `/api/chat`
  - `/api/compare`
- 반복 폐업 지수 샘플 계산 스크립트
- PostgreSQL DDL 초안
- 발표 시연용 Mock 데이터

## 실행 방법

### 1. 백엔드 실행

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

백엔드 확인:

```bash
http://localhost:8000/api/health
```

FastAPI 문서:

```bash
http://localhost:8000/docs
```

### 2. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

프론트엔드 접속:

```bash
http://localhost:5173
```

## 발표 시연 흐름

1. 메인 화면에서 업종 `카페`, 지역 `수원시 영통구` 선택
2. 분석 시작 클릭
3. 상권 분석 대시보드에서 종합 점수와 반복 폐업 지수 확인
4. 반복 폐업 레드존 화면에서 Heatmap과 위험 라벨 확인
5. AI 리포트 화면에서 리포트 생성 확인
6. 추가 Q&A에서 “프랜차이즈로 들어가면 위험이 줄어들까?” 질문
7. 후보지 비교 화면에서 수원 영통구 / 수원 권선구 / 성남 분당구 비교

## 반복 폐업 지수 샘플 계산

```bash
cd backend
python scripts/calc_repeat_closure.py --input data/sample_closure_data.csv --output data/repeat_closure_result.csv
```

결과 파일:

```bash
backend/data/repeat_closure_result.csv
```

## 실제 공공데이터 연결 시 교체할 부분

1. `backend/data/sample_closure_data.csv`를 실제 인허가 CSV로 교체
2. 컬럼명을 아래 표준명으로 맞추기
   - `business_name`
   - `business_type_id`
   - `status`
   - `opened_at`
   - `closed_at`
   - `address_clean`
   - `latitude`
   - `longitude`
   - `geocode_status`
3. `calc_repeat_closure.py` 실행
4. 결과를 DB의 `closure_clusters`, `redzone_points`에 적재

## MVP 설계 결정

- 임대료/예산 정밀 분석은 MVP에서 제외하거나 `null` 처리
- 핵심은 반복 폐업 지수, 경쟁도, 레드존 지도, AI 리포트
- AI 리포트는 현재 Mock으로 작동하며, `.env`에 API 키를 넣고 `report_service.py`를 교체하면 실제 LLM 연동 가능

## 폴더 구조

```text
changup-nachimban/
├─ backend/
│  ├─ app/
│  ├─ data/
│  ├─ scripts/
│  └─ sql/
├─ frontend/
│  └─ src/
└─ docs/
```
