# PRD — Bank Soal + Buku Digital Bahasa Inggris (v1) — Bagian 6
**Tanggal:** 31 Agustus 2025  
**Penulis:** Imam × ChatGPT  
**Status:** Draft untuk MVP

---

# Bagian 6 — Arsitektur, API, Data, Keamanan & Rencana Rilis

### 6.1 Tech Stack
- **Frontend:** Next.js + TypeScript, PWA dengan offline capability, i18n (ID/EN), mobile-first responsive design.  
- **Backend:** FastAPI (Python 3.11+) dengan async/await optimization.  
- **Database:** PostgreSQL 15+ (JSONB untuk konten) dengan read replicas.  
- **Cache/Queue:** Redis (review scheduling, rate limit, search cache).  
- **Storage:** S3/GCS untuk media aset dengan CDN integration.  
- **Search:** Postgres FTS + Redis cache (MVP), ElasticSearch (V2).  
- **Auth:** JWT short-lived + refresh token, RBAC role-based.
- **Analytics:** ClickHouse untuk event analytics, Grafana untuk monitoring.
- **AI/ML:** Python scikit-learn untuk predictive models, OpenAI API untuk content assistance.

### 6.2 API (contoh endpoint utama)
- **Auth:** `POST /auth/login`, `POST /auth/refresh`  
- **Lesson:** `GET /lessons`, `GET /lessons/{id}`  
- **Question:** `GET /questions`, `POST /attempts` (scoring & feedback)  
- **SRS:** `GET /srs/queue`, `POST /srs/review`  
- **Tryout:** `POST /tryouts`, `GET /tryouts/{id}`, `POST /tryouts/{id}/submit`  
- **Progress:** `GET /progress/summary`  
- **Admin:** `POST /admin/lessons`, `POST /admin/questions/import`, `POST /admin/publish`

### 6.3 Skema Data (DDL ringkas)
```sql
-- Users
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  username TEXT UNIQUE,
  password_hash TEXT,
  locale TEXT DEFAULT 'id',
  created_at TIMESTAMP DEFAULT now()
);

-- Roles
CREATE TABLE roles (
  role_id SERIAL PRIMARY KEY,
  name TEXT UNIQUE
);
CREATE TABLE user_roles (
  user_id UUID REFERENCES users(user_id),
  role_id INT REFERENCES roles(role_id),
  PRIMARY KEY (user_id, role_id)
);

-- Lessons
CREATE TABLE lessons (
  lesson_id TEXT PRIMARY KEY,
  title TEXT,
  level TEXT,
  skills TEXT[],
  topics TEXT[],
  objectives JSONB,
  sections JSONB,
  srs_items TEXT[],
  status TEXT,
  version TEXT DEFAULT '1.0.0',
  updated_at TIMESTAMP DEFAULT now()
);

-- Questions
CREATE TABLE questions (
  question_id TEXT PRIMARY KEY,
  type TEXT,
  skill TEXT,
  topics TEXT[],
  level TEXT,
  difficulty INT,
  stem TEXT,
  options JSONB,
  answer_key JSONB,
  meta JSONB,
  status TEXT,
  updated_at TIMESTAMP DEFAULT now()
);

-- Attempts
CREATE TABLE attempts (
  attempt_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id),
  question_id TEXT REFERENCES questions(question_id),
  submitted JSONB,
  correct BOOLEAN,
  time_spent_ms INT,
  created_at TIMESTAMP DEFAULT now()
);

-- SRS State
CREATE TABLE srs_state (
  user_id UUID REFERENCES users(user_id),
  item_id TEXT,
  ease NUMERIC DEFAULT 2.5,
  interval_days INT DEFAULT 1,
  due_at TIMESTAMP,
  PRIMARY KEY (user_id, item_id)
);

-- Sets/Tryouts
CREATE TABLE question_sets (
  set_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(user_id),
  name TEXT,
  question_ids TEXT[],
  settings JSONB,
  created_at TIMESTAMP DEFAULT now()
);

-- Events
CREATE TABLE events (
  event_id UUID PRIMARY KEY,
  user_id UUID,
  type TEXT,
  payload JSONB,
  ts TIMESTAMP DEFAULT now()
);
```

### 6.4 Kinerja & Reliabilitas
- **Target Time-to-Interactive:** < 2.5s (4G), < 1.5s (WiFi).  
- **Target P95 response:** < 400 ms untuk `GET /questions` dengan 50k soal.  
- **Mobile performance:** < 2s lesson load time pada 3G connection.
- **Uptime target:** 99.5% untuk MVP, 99.9% untuk V2.  
- **Scalability:** Support 1000 concurrent users (MVP), 10k (V2).
- Observability: logging terstruktur, tracing dengan request-id, dasbor error real-time.

**Performance Monitoring:**
```json
{
  "core_metrics": {
    "api_response_time_p95": "< 400ms",
    "database_query_time_p95": "< 100ms",
    "cache_hit_rate": "> 80%",
    "cdn_cache_hit_rate": "> 90%"
  },
  "user_experience_metrics": {
    "time_to_first_question": "< 30s",
    "lesson_load_time": "< 2s",
    "search_response_time": "< 500ms",
    "offline_sync_time": "< 10s"
  }
}
```

### 6.5 Keamanan & Privasi
- Password hashing: Argon2/bcrypt.  
- JWT rotasi token, rate limit login brute force.  
- RBAC ketat di admin endpoint; audit log semua perubahan konten.  
- PII minimal, enkripsi at-rest & in-transit.  
- GDPR-lite: export & delete akun.

### 6.6 Rencana Rilis
**MVP (8–10 minggu):**  
- 20–30 Lesson (A1–A2), 300–500 soal dengan content prioritization matrix
- Semua tipe soal MVP, bank soal + filter, tryout sederhana
- CMS author dengan automated validation, review, publish, import CSV
- SRS dasar dengan A/B testing framework, progres sederhana
- PWA dengan offline capability, mobile-first design
- Basic gamification (streaks, achievements)
- Performance monitoring dan analytics foundation

**V1.5 (2-3 minggu post-MVP):**
- Search optimization dengan Redis caching
- Advanced personalization engine
- Predictive churn detection
- Enhanced mobile experience

**V2 (3-4 bulan):**
- Listening mikro dengan TTS integration
- ElasticSearch dengan semantic search
- Advanced analytics dan content effectiveness measurement
- Social learning features (study groups, leaderboards)
- AI-powered content suggestions

**V3 (6-8 bulan):**
- Classroom/instansi management
- Assignment guru dengan bulk operations
- Advanced AI tutoring features
- Real-time collaboration tools
- Enterprise-grade security dan compliance

### 6.7 QA & Acceptance
- Black-box test semua tipe soal & feedback.  
- Content linting wajib lolos sebelum publish.  
- Load test 100 RPS untuk `GET /questions` p95 < 400 ms.  
- Security test (OWASP top 10 dasar).  
- Pilot 100 pengguna: retensi D7 ≥ 20%, bug blocker = 0.

### 6.8 Risiko & Mitigasi
**Technical Risks:**
- **Search performance bottleneck:** Implement aggressive caching strategy, prepare ElasticSearch migration path
- **Database scalability:** Use read replicas, implement connection pooling, prepare sharding strategy
- **Mobile performance issues:** Implement PWA caching, optimize bundle size, use lazy loading
- **Content delivery latency:** CDN integration dari awal, image optimization pipeline

**Product Risks:**
- **Content quality inconsistency:** Automated validation pipeline + native speaker review process
- **User engagement drop:** Gamification elements + personalization engine + churn prediction
- **Competition from established players:** Focus on Indonesian learner-specific needs + superior content depth
- **Monetization challenges:** Clear freemium model dengan value proposition yang jelas

**Business Risks:**
- **Content creation bottleneck:** Template-based authoring + community contribution system
- **User acquisition cost:** Organic growth strategy + referral program + content marketing
- **Retention challenges:** SRS optimization + adaptive learning + intervention system

### 6.9 Pertanyaan Terbuka & Decisions Needed
**Technical Decisions:**
- LaTeX support untuk phonetics/IPA: Start dengan Unicode IPA symbols, evaluate LaTeX need based on user feedback
- Listening implementation: Begin dengan TTS (cost-effective), upgrade ke native recordings based on user engagement
- AI integration level: Start dengan rule-based systems, gradually introduce ML models

**Product Decisions:**
- Monetization model: Implement freemium dengan clear value tiers (decided: Rp 49k/month Pro tier)
- Content localization depth: Full bilingual vs English-focused dengan Indonesian explanations
- Social features priority: Individual learning first, social features dalam V2

**Business Decisions:**
- Target market focus: B2C individual learners vs B2B institutional sales
- Content partnership strategy: In-house creation vs licensed content vs community-generated
- Geographic expansion: Indonesia-first vs regional SEA expansion timeline

### 6.10 Implementation Roadmap
**Phase 1: Foundation (Week 1-4)**
- Core architecture setup (Next.js + FastAPI + PostgreSQL)
- Basic authentication dan RBAC
- Content management system dengan validation pipeline
- Database schema implementation dengan sample data

**Phase 2: Core Features (Week 5-8)**
- Lesson delivery system dengan mobile optimization
- Question types implementation dengan scoring
- Basic SRS algorithm dengan A/B testing framework
- Search functionality dengan caching strategy

**Phase 3: Enhancement (Week 9-10)**
- PWA implementation dengan offline capability
- Gamification elements (streaks, achievements)
- Analytics integration dan monitoring setup
- Performance optimization dan load testing

**Phase 4: Polish & Launch (Week 11-12)**
- Content seeding dengan prioritization matrix
- User acceptance testing dengan pilot group
- Security audit dan penetration testing
- Production deployment dengan monitoring

### 6.11 Success Metrics Tracking
**MVP Success Criteria:**
```json
{
  "user_engagement": {
    "daily_active_users": "target: 100+ by week 4",
    "session_duration": "target: 15+ minutes average",
    "lesson_completion_rate": "target: 55%+",
    "return_rate_d7": "target: 20%+"
  },
  "technical_performance": {
    "api_response_time_p95": "< 400ms",
    "uptime": "> 99.5%",
    "error_rate": "< 1%",
    "mobile_performance_score": "> 80"
  },
  "content_quality": {
    "content_validation_pass_rate": "> 95%",
    "user_feedback_score": "> 4.0/5",
    "question_accuracy_alignment": "> 90%",
    "native_speaker_approval_rate": "> 95%"
  }
}
```

**Post-Launch Optimization:**
- Weekly performance reviews dengan data-driven decisions
- Monthly content effectiveness analysis
- Quarterly user research untuk feature prioritization
- Continuous A/B testing untuk conversion optimization