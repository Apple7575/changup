import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AlertTriangle, BarChart3, Bot, Building2, Compass, Database, FileText, MapPinned, MessageCircle, ShieldCheck, Sparkles, Store, TrendingUp } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from './api/client';
import './styles.css';

const DEFAULT_ANALYSIS = 'ANL-CAFE-GG-SUWON-YEONGTONG';

function Header({ current, setCurrent }) {
  const tabs = [
    ['home', '대시보드'],
    ['analysis', '상권 분석'],
    ['redzone', '반복 폐업 분석'],
    ['report', 'AI 리포트'],
    ['compare', '후보지 비교'],
    ['system', '작동 구조'],
  ];
  return (
    <header className="header">
      <div className="logo"><div className="logo-icon"><Compass size={20} /></div>창업나침반 경기</div>
      <nav className="nav">
        {tabs.map(([key, label]) => <button key={key} className={current === key ? 'active' : ''} onClick={() => setCurrent(key)}>{label}</button>)}
      </nav>
    </header>
  );
}

function Feature({ icon, title, desc }) {
  return <div className="feature">{icon}<div><b>{title}</b><p>{desc}</p></div></div>;
}

function Metric({ title, value, state = '보통', level = 'medium', icon }) {
  return <div className="metric"><div className="k">{icon}{title}</div><div className="v">{value}</div><span className={`badge ${level}`}>{state}</span></div>;
}

function App() {
  const [current, setCurrent] = useState('home');
  const [businessTypes, setBusinessTypes] = useState([]);
  const [regions, setRegions] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState('CAFE');
  const [selectedRegion, setSelectedRegion] = useState('GG-SUWON-YEONGTONG');
  const [analysis, setAnalysis] = useState(null);
  const [redzones, setRedzones] = useState(null);
  const [report, setReport] = useState(null);
  const [chatAnswer, setChatAnswer] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);

  useEffect(() => {
    api.getBusinessTypes().then(data => setBusinessTypes(data.business_types)).catch(console.error);
    api.getRegions().then(data => setRegions(data.regions)).catch(console.error);
    api.analyze({ business_type_id: 'CAFE', region_id: 'GG-SUWON-YEONGTONG', include_redzone_summary: true })
      .then(data => setAnalysis(data)).catch(console.error);
  }, []);

  const runAnalyze = async () => {
    const data = await api.analyze({ business_type_id: selectedBusiness, region_id: selectedRegion, include_redzone_summary: true });
    setAnalysis(data);
    setReport(null);
    setChatAnswer(null);
    setCurrent('analysis');
  };

  const loadRedzones = async () => {
    const target = analysis || await api.getAnalysis(DEFAULT_ANALYSIS);
    setAnalysis(target);
    const data = await api.getRedzones({ business_type_id: target.business_type.business_type_id, region_id: target.region.region_id });
    setRedzones(data);
  };

  const loadReport = async () => {
    if (!analysis) return;
    setLoadingReport(true);
    setCurrent('report');
    try {
      const data = await api.report({
        analysis_id: analysis.analysis_id,
        business_type: analysis.business_type,
        region: analysis.region,
        score_summary: analysis.score_summary,
        scores: analysis.scores,
        redzone_summary: analysis.redzone_summary,
        risk_labels: analysis.risk_labels,
      });
      setReport(data);
    } finally {
      setLoadingReport(false);
    }
  };

  return <div className="app-shell"><Header current={current} setCurrent={setCurrent} />
    <main className="container">
      {current === 'home' && <Home businessTypes={businessTypes} regions={regions} selectedBusiness={selectedBusiness} setSelectedBusiness={setSelectedBusiness} selectedRegion={selectedRegion} setSelectedRegion={setSelectedRegion} runAnalyze={runAnalyze} />}
      {current === 'analysis' && <Dashboard analysis={analysis} setCurrent={setCurrent} loadReport={loadReport} loadRedzones={loadRedzones} />}
      {current === 'redzone' && <Redzone analysis={analysis} redzones={redzones} loadRedzones={loadRedzones} />}
      {current === 'report' && <Report analysis={analysis} report={report} loading={loadingReport} loadReport={loadReport} setChatAnswer={setChatAnswer} chatAnswer={chatAnswer} />}
      {current === 'compare' && <Compare />}
      {current === 'system' && <SystemFlow />}
    </main>
  </div>;
}

function Home({ businessTypes, regions, selectedBusiness, setSelectedBusiness, selectedRegion, setSelectedRegion, runAnalyze }) {
  return <>
    <section className="hero">
      <div className="card">
        <h1 className="title">업종과 지역을 선택하면<br /><span>창업 위험</span>을 바로 진단합니다</h1>
        <p className="subtitle">경기도 공공데이터와 AI 분석으로 반복 폐업 위험 입지를 미리 확인하고, 감이 아닌 데이터로 창업 의사결정을 돕습니다.</p>
        <div className="form-grid">
          <div><div className="label-row"><strong>업종 선택</strong><small>분석할 업종을 선택하세요</small></div>
            <div className="chips">{businessTypes.map(bt => <button className={`chip ${selectedBusiness === bt.business_type_id ? 'active' : ''}`} key={bt.business_type_id} onClick={() => setSelectedBusiness(bt.business_type_id)}>{bt.name}</button>)}</div>
          </div>
          <div><div className="label-row"><strong>지역 선택</strong><small>분석할 지역을 선택하세요</small></div>
            <div className="select-row"><select value={selectedRegion} onChange={e => setSelectedRegion(e.target.value)}>{regions.map(r => <option key={r.region_id} value={r.region_id}>{r.display_name}</option>)}</select><button className="secondary"><MapPinned size={16} /> 지도에서 선택</button></div>
          </div>
          <button className="primary" onClick={runAnalyze}><Sparkles size={18} /> 분석 시작</button>
        </div>
      </div>
      <div className="card">
        <h3>추천 분석 항목</h3>
        <div className="feature-list">
          <Feature icon={<BarChart3 />} title="상권 점수" desc="유동인구, 접근성, 경쟁도를 종합 평가" />
          <Feature icon={<Store />} title="경쟁도" desc="동일 업종 밀집도와 포화도 분석" />
          <Feature icon={<AlertTriangle />} title="반복 폐업 지수" desc="과거 폐업 패턴 기반 위험도 분석" />
          <Feature icon={<MapPinned />} title="레드존 지도" desc="반복 폐업 다발 구역을 Heatmap으로 표시" />
        </div>
      </div>
    </section>
    <section className="steps">
      {['업종 선택', '지역 선택', '데이터 분석', 'AI 리포트'].map((s, i) => <div className="step" key={s}><div className="step-num">{i + 1}</div><b>{s}</b><p className="footer-note">{i === 2 ? '공공데이터와 AI로 정밀 분석' : '간편하게 진행'}</p></div>)}
    </section>
  </>;
}

function Dashboard({ analysis, setCurrent, loadReport, loadRedzones }) {
  if (!analysis) return <div className="card">분석 데이터를 불러오는 중입니다.</div>;
  const { scores, score_summary, redzone_summary, key_metrics } = analysis;
  return <>
    <h1 className="title">상권 분석 대시보드</h1>
    <p className="subtitle">업종: {analysis.business_type.name} | 지역: {analysis.region.display_name} | analysis_id: {analysis.analysis_id}</p>
    <div className="dashboard-grid">
      <Metric title="종합 점수" value={`${score_summary.total_score}/100`} state={score_summary.decision} level="medium" icon={<TrendingUp size={16} />} />
      <Metric title="유동인구" value={`${scores.floating_population}/100`} state="양호" level="good" icon={<BarChart3 size={16} />} />
      <Metric title="경쟁도" value={`${scores.competition}/100`} state="보통" level="medium" icon={<Store size={16} />} />
      <Metric title="반복 폐업" value={`${scores.repeat_closure}/100`} state={redzone_summary.risk_level === 'HIGH' ? '위험' : '보통'} level={redzone_summary.risk_level === 'HIGH' ? 'high' : 'medium'} icon={<AlertTriangle size={16} />} />
    </div>
    <div className="content-grid">
      <div className="card map-card"><FakeMap label={redzone_summary.top_label} /></div>
      <div className="card">
        <h3>상권 핵심 요약</h3>
        <div className="summary-list">
          <div className="summary-row"><span>일평균 유동인구</span><span>{key_metrics.daily_floating_population.toLocaleString()}명</span></div>
          <div className="summary-row"><span>20대 유동인구 비율</span><span>{key_metrics.age_20_ratio}%</span></div>
          <div className="summary-row"><span>동일 업종 점포 수</span><span>{key_metrics.store_count_same_category}개</span></div>
          <div className="summary-row"><span>최근 3년 폐업률</span><span>{key_metrics.closure_rate_3y}%</span></div>
          <div className="summary-row"><span>24개월 이내 폐업 비율</span><span>{key_metrics.short_term_closure_ratio}%</span></div>
        </div>
        <div style={{display:'flex', gap:10, marginTop:20, flexWrap:'wrap'}}>
          <button className="primary" onClick={async()=>{ await loadRedzones(); setCurrent('redzone'); }}>반복 폐업 레드존 보기</button>
          <button className="secondary" onClick={loadReport}>AI 리포트 생성</button>
        </div>
      </div>
    </div>
  </>;
}

function FakeMap({ label='카페 반복 폐업 위험 지역' }) {
  return <div className="fake-map"><div className="grid-line" /><div className="marker one"><span>!</span></div><div className="marker two"><span>!</span></div><div className="map-popup"><b>{label}</b><small>반복 폐업 지수 87 / 위험</small></div></div>;
}

function Redzone({ analysis, redzones, loadRedzones }) {
  useEffect(() => { if (!redzones) loadRedzones(); }, []);
  if (!analysis) return <div className="card">먼저 상권 분석을 진행해주세요.</div>;
  const summary = analysis.redzone_summary;
  const marker = redzones?.warning_markers?.[0];
  return <>
    <h1 className="title">반복 폐업 레드존 분석</h1>
    <p className="subtitle">데이터로 발견하는 반복 폐업 패턴. URL 컨텍스트 예시: /redzone?analysis_id={analysis.analysis_id}</p>
    <div className="dashboard-grid">
      <Metric title="반복 폐업 지수" value={`${summary.repeat_closure_score}/100`} state="위험" level="high" icon={<AlertTriangle size={16} />} />
      <Metric title="단기 폐업 비율" value={`${summary.short_term_closure_ratio}%`} state="보통" level="medium" icon={<BarChart3 size={16} />} />
      <Metric title="동일 업종 재폐업" value={`${summary.same_category_reclosure_ratio}%`} state="위험" level="high" icon={<Store size={16} />} />
      <Metric title="동일 입지 재폐업" value={`${summary.same_location_reclosure_ratio}%`} state="위험" level="high" icon={<MapPinned size={16} />} />
    </div>
    <div className="content-grid">
      <div className="card map-card"><FakeMap label={summary.top_label} /></div>
      <div className="card">
        <h3>위험 지역 상세</h3>
        <p className="subtitle" style={{marginBottom:8}}>{marker?.title || summary.top_label}</p>
        <div className="summary-list">
          <div className="summary-row"><span>반복 폐업 업소 수</span><span>{marker?.closed_store_count || summary.closed_store_count}개</span></div>
          <div className="summary-row"><span>24개월 이내 폐업 비율</span><span>{marker?.short_term_closure_ratio || summary.short_term_closure_ratio}%</span></div>
          <div className="summary-row"><span>동일 업종 재폐업</span><span>{marker?.same_category_reclosure_ratio || summary.same_category_reclosure_ratio}%</span></div>
          <div className="summary-row"><span>동일 입지 재폐업</span><span>{marker?.same_location_reclosure_ratio || summary.same_location_reclosure_ratio}%</span></div>
        </div>
        <div className="report-section" style={{marginTop:14}}><h4>폐업 패턴 타임라인</h4><p>개업 102건 → 폐업 61건 → 재개업 34건 → 재폐업 19건<br/>재개업 후 다시 폐업한 비율: 55.9%</p></div>
      </div>
    </div>
  </>;
}

function Report({ analysis, report, loading, loadReport, setChatAnswer, chatAnswer }) {
  const [question, setQuestion] = useState('프랜차이즈로 들어가면 위험이 줄어들까?');
  useEffect(() => { if (analysis && !report && !loading) loadReport(); }, []);
  const ask = async (q = question) => {
    if (!analysis) return;
    const data = await api.chat({ analysis_id: analysis.analysis_id, report_id: report?.report_id, question: q, analysis_snapshot: { business_type: analysis.business_type.name, region: analysis.region.display_name, scores: analysis.scores, risk_labels: analysis.risk_labels } });
    setChatAnswer(data);
  };
  if (!analysis) return <div className="card">분석 결과가 없습니다.</div>;
  return <>
    <h1 className="title">AI 상권 생존 리포트</h1>
    <p className="subtitle">AI가 공공데이터 기반으로 위험 요인과 운영 전략을 설명합니다. 10초 이상 지연 시 기본 리포트로 대체합니다.</p>
    <div className="content-grid">
      <div className="card">
        <Metric title="종합 생존 점수" value={`${analysis.score_summary.total_score}/100`} state={analysis.score_summary.decision} level="medium" icon={<ShieldCheck size={16}/>} />
        <div style={{height:260, marginTop:20}}><ResponsiveContainer width="100%" height="100%"><BarChart data={Object.entries(analysis.scores).filter(([,v])=>v!==null).map(([name,value])=>({name, value}))}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="value" fill="#2563eb" radius={[8,8,0,0]}/></BarChart></ResponsiveContainer></div>
      </div>
      <div className="card">
        <h3>AI 종합 리포트</h3>
        {loading && <><div className="skeleton"/><div className="skeleton" style={{width:'80%'}}/><div className="skeleton" style={{width:'60%'}}/></>}
        {!loading && report?.sections?.map(s => <div className="report-section" key={s.section_id}><h4>{s.title}</h4><p>{s.content}</p></div>)}
      </div>
    </div>
    <div className="card" style={{marginTop:18}}>
      <h3>추가 질의응답</h3>
      <div className="quick-questions">{['프랜차이즈로 들어가면 위험이 줄어들까?','20대 유동인구만 보면 어때?','대체 지역은 왜 추천한 거야?'].map(q=><button key={q} onClick={()=>{setQuestion(q); ask(q);}}>{q}</button>)}</div>
      <div className="chat-input"><input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="궁금한 내용을 입력하세요"/><button className="primary" onClick={()=>ask()}>전송</button></div>
      {chatAnswer && <div className="chat-box" style={{marginTop:14}}><div className="message">{chatAnswer.question}</div><div className="message ai"><b>AI 답변</b><br/>{chatAnswer.answer}<br/><br/><b>근거 지표</b><br/>{chatAnswer.evidence.map(e=>`${e.metric}: ${e.value} / ${e.interpretation}`).join(' · ')}</div></div>}
    </div>
  </>;
}

function Compare() {
  const [data, setData] = useState(null);
  useEffect(() => { api.compare({ business_type_id: 'CAFE', region_ids: ['GG-SUWON-YEONGTONG','GG-SUWON-GWONSEON','GG-SEONGNAM-BUNDANG'], use_cache: true }).then(setData).catch(console.error); }, []);
  const items = data?.comparison || [];
  return <>
    <h1 className="title">후보 입지 비교</h1>
    <p className="subtitle">동일 업종·동일 지역은 모든 화면에서 동일한 분석 점수를 재사용합니다.</p>
    <div className="compare-grid">{items.map((item, idx)=><div className={`compare-card ${idx===0?'best':''}`} key={item.region_id}>
      <span className={`badge ${item.recommendation==='추천'?'good': item.recommendation==='비추천'?'high':'medium'}`}>{item.recommendation}</span>
      <div className="compare-title">{item.display_name}</div>
      {Object.entries(item.scores).filter(([,v])=>v!==null).map(([k,v])=><div key={k}><div className="summary-row"><span>{k}</span><span>{v}</span></div><div className="bar"><div style={{width:`${v}%`}} /></div></div>)}
      <p className="footer-note">{item.ai_summary}</p>
    </div>)}</div>
  </>;
}

function SystemFlow() {
  const blocks = [
    ['공공데이터 수집', '상가업소 정보, 인허가 데이터, 유동인구, 교통 데이터', <Database/>],
    ['데이터 정제', '주소 정제, 좌표 변환, 업종 코드 매핑, 결측치 처리', <Building2/>],
    ['반복 폐업 분석', '좌표 기반 클러스터링, 반복 폐업 지수, 레드존 산출', <AlertTriangle/>],
    ['AI 리포트 생성', '분석 JSON → 동적 프롬프트 → AI 생존 리포트', <Bot/>],
    ['의사결정 지원', '대시보드, 레드존 지도, AI 리포트, Q&A, 후보지 비교', <FileText/>],
  ];
  return <><h1 className="title">창업나침반 경기 작동 구조</h1><p className="subtitle">공공데이터를 단순 조회가 아니라 반복 폐업 패턴 분석과 창업 의사결정으로 연결합니다.</p><div className="steps" style={{gridTemplateColumns:'repeat(5,1fr)'}}>{blocks.map(([t,d,i],idx)=><div className="step" key={t}><div className="step-num">{idx+1}</div><div style={{color:'#2563eb'}}>{i}</div><b>{t}</b><p className="footer-note">{d}</p></div>)}</div></>;
}

createRoot(document.getElementById('root')).render(<App />);
