-- 창업나침반 경기 MVP schema v1.1 핵심 DDL
CREATE TABLE IF NOT EXISTS regions (
    id BIGSERIAL PRIMARY KEY,
    region_id VARCHAR(50) UNIQUE NOT NULL,
    sido VARCHAR(50) NOT NULL,
    sigungu VARCHAR(100) NOT NULL,
    dong VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS business_types (
    id BIGSERIAL PRIMARY KEY,
    business_type_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    source_category_codes JSONB,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS license_records (
    id BIGSERIAL PRIMARY KEY,
    source_license_id VARCHAR(100),
    business_name VARCHAR(200) NOT NULL,
    business_type_id VARCHAR(50) REFERENCES business_types(business_type_id),
    source_category_name VARCHAR(200),
    source_category_code VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    opened_at DATE,
    closed_at DATE,
    region_id VARCHAR(50) REFERENCES regions(region_id),
    address_raw TEXT,
    address_clean TEXT,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    geocode_status VARCHAR(50) DEFAULT 'PENDING',
    operation_months INTEGER,
    is_short_term_closed BOOLEAN DEFAULT false,
    data_reference_date DATE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    CONSTRAINT chk_geocode_status CHECK (geocode_status IN ('PENDING', 'SUCCESS', 'FAILED')),
    CONSTRAINT chk_license_status CHECK (status IN ('OPEN', 'CLOSED', 'SUSPENDED', 'UNKNOWN'))
);

CREATE TABLE IF NOT EXISTS closure_clusters (
    id BIGSERIAL PRIMARY KEY,
    cluster_id VARCHAR(100) UNIQUE NOT NULL,
    region_id VARCHAR(50) REFERENCES regions(region_id),
    business_type_id VARCHAR(50) REFERENCES business_types(business_type_id),
    center_latitude DECIMAL(10,7) NOT NULL,
    center_longitude DECIMAL(10,7) NOT NULL,
    radius_m INTEGER DEFAULT 100,
    closure_count INTEGER DEFAULT 0,
    short_term_closure_count INTEGER DEFAULT 0,
    reopen_count INTEGER DEFAULT 0,
    reclosure_count INTEGER DEFAULT 0,
    short_term_closure_ratio DECIMAL(5,2) DEFAULT 0,
    same_location_reclosure_ratio DECIMAL(5,2) DEFAULT 0,
    same_category_reclosure_ratio DECIMAL(5,2) DEFAULT 0,
    repeat_closure_score INTEGER DEFAULT 0,
    risk_level VARCHAR(20) DEFAULT 'LOW',
    pattern_label VARCHAR(200),
    source_record_count INTEGER DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT now(),
    created_at TIMESTAMP DEFAULT now(),
    CONSTRAINT chk_cluster_risk_level CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH'))
);

CREATE TABLE IF NOT EXISTS redzone_points (
    id BIGSERIAL PRIMARY KEY,
    marker_id VARCHAR(100) UNIQUE NOT NULL,
    cluster_id VARCHAR(100) REFERENCES closure_clusters(cluster_id),
    region_id VARCHAR(50) REFERENCES regions(region_id),
    business_type_id VARCHAR(50) REFERENCES business_types(business_type_id),
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    weight DECIMAL(4,2) DEFAULT 0,
    risk_level VARCHAR(20) DEFAULT 'LOW',
    title VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP DEFAULT now(),
    CONSTRAINT chk_redzone_risk_level CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH'))
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id BIGSERIAL PRIMARY KEY,
    analysis_id VARCHAR(100) UNIQUE NOT NULL,
    region_id VARCHAR(50) REFERENCES regions(region_id),
    business_type_id VARCHAR(50) REFERENCES business_types(business_type_id),
    total_score INTEGER NOT NULL,
    decision_code VARCHAR(20) NOT NULL,
    decision_label VARCHAR(50) NOT NULL,
    survival_probability INTEGER,
    floating_population_score INTEGER,
    competition_score INTEGER,
    repeat_closure_score INTEGER,
    rent_burden_score INTEGER,
    accessibility_score INTEGER,
    risk_labels JSONB,
    key_metrics JSONB,
    redzone_summary JSONB,
    map_config JSONB,
    data_reference_date DATE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    CONSTRAINT chk_decision_code CHECK (decision_code IN ('GOOD', 'NORMAL', 'CAUTION', 'DANGER'))
);

CREATE INDEX IF NOT EXISTS idx_license_geocode_success ON license_records(region_id, business_type_id, status, geocode_status) WHERE geocode_status = 'SUCCESS';
CREATE INDEX IF NOT EXISTS idx_license_location_success ON license_records(latitude, longitude) WHERE geocode_status = 'SUCCESS';
CREATE INDEX IF NOT EXISTS idx_cluster_region_business ON closure_clusters(region_id, business_type_id);
CREATE INDEX IF NOT EXISTS idx_redzone_region_business ON redzone_points(region_id, business_type_id);
CREATE INDEX IF NOT EXISTS idx_analysis_region_business ON analysis_results(region_id, business_type_id);
CREATE INDEX IF NOT EXISTS idx_analysis_expires_at ON analysis_results(expires_at);
