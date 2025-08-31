# PRD — Bank Soal + Buku Digital Bahasa Inggris (v1) — Bagian 2
**Tanggal:** 31 Agustus 2025  
**Penulis:** Imam × ChatGPT  
**Status:** Draft untuk MVP

---

# Bagian 2 — Desain Pembelajaran & Format Konten

### 2.1 Taksonomi Konten
- **Level:** CEFR A1–C2 (MVP fokus A1–B2).  
- **Skill:** Grammar, Vocabulary, Reading (Listening masuk V2).  
- **Topik:** Travel, Work, Food, Daily Life, Academic, dsb.  
- **Tag:** tense, function (advice, obligation), part of speech, difficulty 1–5.

### 2.2 Struktur Unit (seperti buku)
**Path → Unit → Lesson → Section**

- **Lesson Sections:**  
  1. **Concept:** definisi singkat, formula grammar, rumus.  
  2. **Examples:** contoh EN→ID.  
  3. **Common Errors:** kesalahan yang sering terjadi.  
  4. **Guided Practice:** latihan ringan.  
  5. **Free Practice:** latihan lebih menantang.  
  6. **Mini Review:** 3–5 soal kunci + push ke SRS.

### 2.3 Pedagogi
- *Comprehensible Input + Retrieval Practice + Spaced Repetition*.  
- Materi singkat (≤ 250 kata/section), mobile-optimized.  
- Setiap konsep → langsung ada latihan.  
- Feedback kesalahan selalu muncul dengan rule card + contoh benar.
- **Adaptive Learning:** Difficulty adjustment berdasarkan accuracy rate.
- **Personalization:** Learning path disesuaikan dengan weakness detection.
- **Gamification:** Streaks, achievements, dan progress visualization.

### 2.4 Tipe Soal (MVP)
- **MCQ** (single/multi).  
- **Cloze/Gap-fill.**  
- **Ordering.**  
- **Error Detection/Correction.**  
- **Short Answer** (regex + model answer).

### 2.5 Contoh Struktur Data
**Lesson JSON (ringkas):**
```json
{
  "lesson_id": "L1_SimplePresent",
  "title": "Simple Present Tense",
  "level": "A1",
  "skill": ["grammar"],
  "sections": [
    {"type":"concept","heading":"Rumus Dasar","body":"S + V1 (+s/es untuk he/she/it)"},
    {"type":"examples","items":[{"en":"She plays tennis.","id":"Dia bermain tenis."}]},
    {"type":"common_errors","items":[{"wrong":"She play tennis.","why":"Harus plays."}]}
  ],
  "exercises": ["Q_GRM_001","Q_GRM_002"],
  "srs_items": ["rule_simple_present","verb_play"]
}
```

**Question JSON (contoh MCQ):**
```json
{
  "question_id": "Q_GRM_001",
  "type": "mcq",
  "stem": "Choose the correct sentence:",
  "options": [
    {"id":"A","text":"He go to school every day.","explain":"Harus goes."},
    {"id":"B","text":"He goes to school every day.","correct":true,"explain":"Benar."}
  ],
  "answer_key": ["B"]
}
```

### 2.6 Acceptance Criteria
- Setiap lesson minimal 3 section (Concept, Examples, Common Errors).  
- Setiap lesson minimal 5 soal dengan feedback.  
- Semua tipe soal MVP bisa dijawab dengan feedback konsisten.  
- Lesson bisa dipublish dan ditarik lewat API.
- **Mobile-first:** Semua konten responsive dan touch-optimized.
- **Offline capability:** Core lessons bisa diakses offline setelah download.
- **Performance:** Lesson load time < 2 detik pada koneksi 3G.
- **Content validation:** Automated linting untuk grammar, consistency, dan difficulty alignment.


### 2.7 Gamification Elements
**Achievement System:**
```json
{
  "streaks": {
    "daily_study": "consecutive days studying",
    "perfect_scores": "100% accuracy streak",
    "review_consistency": "SRS reviews completed on time"
  },
  "badges": {
    "grammar_master": "complete all grammar lessons",
    "speed_demon": "answer 10 questions under 30s each",
    "error_detective": "find 50 grammar errors correctly",
    "vocabulary_builder": "learn 500 new words"
  },
  "progress_visualization": {
    "skill_trees": "unlock advanced topics",
    "mastery_levels": "bronze/silver/gold per topic",
    "weekly_goals": "customizable study targets"
  }
}
```

### 2.8 Content Quality Assurance
**Automated Validation Pipeline:**
- **Grammar consistency:** Tense usage, subject-verb agreement
- **Difficulty alignment:** Vocabulary level vs CEFR level
- **Bilingual accuracy:** ID translation quality check
- **Example relevance:** Context appropriateness untuk target audience
- **Common errors authenticity:** Validation dengan native speaker input

**Content Linting Rules:**
```python
# Example validation rules
def validate_lesson_content(lesson):
    checks = [
        check_required_fields(lesson),
        check_cefr_vocabulary_alignment(lesson),
        check_indonesian_translation_quality(lesson),
        check_example_cultural_relevance(lesson),
        check_common_errors_authenticity(lesson)
    ]
    return all(checks)
```