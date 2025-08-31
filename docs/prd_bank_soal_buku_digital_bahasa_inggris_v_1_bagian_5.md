# PRD — Bank Soal + Buku Digital Bahasa Inggris (v1) — Bagian 5
**Tanggal:** 31 Agustus 2025  
**Penulis:** Imam × ChatGPT  
**Status:** Draft untuk MVP

---

# Bagian 5 — Penilaian, SRS, Mastery & Analytics

### 5.1 Penilaian & Skoring
- **MCQ Single:** 1 benar = 1 poin.  
- **MCQ Multi (V2):** bisa parsial (setiap jawaban benar diberi poin).  
- **Cloze:** exact match; daftar sinonim opsional; case-insensitive.  
- **Ordering:** benar = 1 poin; V2 mendukung parsial.  
- **Error Detection/Correction:** regex/posisi; tampilkan kalimat benar.  
- **Short Answer:** regex + model answer.

### 5.2 SRS (Spaced Repetition System)
**Base Algorithm:**
- Tombol feedback: **Again / Hard / Good / Easy**
- `ease` default: 2.5
- Update interval:  
  - Again → interval = 1 hari, ease −0.2  
  - Hard → interval ×1.2, ease −0.05  
  - Good → interval ×ease  
  - Easy → interval ×(ease+0.15), max interval dibatasi sesuai level

**A/B Testing Parameters:**
```json
{
  "test_variants": {
    "conservative": {"initial_ease": 2.0, "max_interval": 180},
    "standard": {"initial_ease": 2.5, "max_interval": 365},
    "aggressive": {"initial_ease": 3.0, "max_interval": 730}
  },
  "success_metrics": [
    "retention_rate_d30",
    "mastery_achievement_rate",
    "daily_review_completion"
  ]
}
```

**Adaptive Features:**
- **Difficulty adjustment:** Auto-adjust based on accuracy patterns
- **Learning velocity:** Faster progression untuk consistent performers
- **Weakness targeting:** Extra reviews untuk problematic concepts
- **Context-aware scheduling:** Consider user's study patterns

### 5.3 Mastery Model
- Per topik/skill, mastery tercapai bila:
  - Akurasi ≥ 80%  
  - Minimal 2 review sukses berjarak ≥ 24 jam  
- Mastery membuka akses ke unit/bab berikutnya.

### 5.4 Analytics & Telemetry
- **Learner analytics:** akurasi per skill/topik, waktu pengerjaan, jumlah review selesai, streak belajar.  
- **Content analytics:** tingkat kesulitan empiris, *discrimination index*, distraktor yang paling sering dipilih, heatmap misconception.  
- **Product analytics:** retensi D1/D7/D30, conversion rate ke Pro, ARPU, churn reason.

**Contoh Skema Event:**
```json
{
  "event_id": "uuid",
  "user_id": "u123",
  "type": "attempt_submitted",
  "question_id": "Q_GRM_001",
  "correct": true,
  "time_spent_ms": 12450,
  "ts": "2025-08-31T06:00:00Z"
}
```

### 5.5 Acceptance Criteria
- Semua tipe soal MVP dapat dihitung skornya secara konsisten.  
- Feedback otomatis muncul setelah attempt.  
- SRS queue berjalan dengan due items muncul sesuai jadwal.  
- Dashboard progres menampilkan kelemahan per skill/topik.  
- Analytics event terkirim dengan format standar (user_id, type, payload, timestamp).
- **A/B Testing:** SRS algorithm parameters dengan cohort validation.
- **Personalization:** Adaptive difficulty berdasarkan performance history.
- **Predictive Analytics:** Early churn detection dan intervention.
- **Real-time Feedback:** Instant performance insights dan recommendations.

### 5.6 Advanced Analytics & Personalization
**Predictive Modeling:**
```python
# Churn prediction model
class ChurnPredictor:
    def predict_churn_risk(self, user_id):
        features = {
            'days_since_last_activity': self.get_activity_gap(user_id),
            'completion_rate_trend': self.get_completion_trend(user_id),
            'srs_adherence_rate': self.get_srs_consistency(user_id),
            'difficulty_frustration_score': self.get_frustration_level(user_id)
        }
        return self.model.predict_proba(features)

    def generate_intervention_strategy(self, churn_risk):
        if churn_risk > 0.7:
            return "immediate_engagement_campaign"
        elif churn_risk > 0.4:
            return "difficulty_adjustment_suggestion"
        else:
            return "standard_encouragement"
```

**Personalized Learning Paths:**
- **Weakness Detection:** Identify struggling concepts automatically
- **Strength Leveraging:** Build confidence through mastered topics
- **Learning Style Adaptation:** Visual vs text-based preferences
- **Pace Optimization:** Adjust content delivery speed per user

### 5.7 Advanced Mastery Tracking
**Multi-dimensional Mastery:**
```json
{
  "mastery_dimensions": {
    "accuracy": "correctness of answers",
    "speed": "time efficiency in responses",
    "retention": "long-term memory consolidation",
    "application": "ability to use in different contexts",
    "confidence": "self-reported understanding level"
  },
  "mastery_levels": {
    "novice": "< 60% accuracy, high variability",
    "developing": "60-79% accuracy, improving consistency",
    "proficient": "80-94% accuracy, stable performance",
    "expert": "95%+ accuracy, teaching-ready level"
  }
}
```

**Adaptive Assessment:**
- **Dynamic Difficulty:** Real-time adjustment based on performance
- **Concept Prerequisite Mapping:** Ensure foundational understanding
- **Spaced Testing:** Distributed practice for long-term retention
- **Transfer Assessment:** Apply knowledge in new contexts

### 5.8 Real-time Intervention System
**Automated Support Triggers:**
```python
class InterventionEngine:
    def monitor_user_session(self, user_id, session_data):
        triggers = {
            'consecutive_failures': session_data.wrong_answers >= 3,
            'time_struggling': session_data.avg_time_per_question > threshold,
            'frustration_indicators': session_data.rapid_clicking or session_data.long_pauses,
            'off_track_learning': session_data.random_topic_jumping
        }
        
        for trigger, condition in triggers.items():
            if condition:
                self.deploy_intervention(user_id, trigger)
```

**Intervention Strategies:**
- **Hint System:** Progressive clues untuk struggling questions
- **Concept Review:** Automatic redirect ke foundational material
- **Difficulty Reduction:** Temporary easier questions untuk confidence building
- **Motivational Messaging:** Personalized encouragement based on progress