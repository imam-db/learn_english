# PRD — Bank Soal + Buku Digital Bahasa Inggris (v1) — Bagian 1
**Tanggal:** 31 Agustus 2025  
**Penulis:** Imam × ChatGPT  
**Status:** Draft untuk MVP

---

# Bagian 1 — Visi, Sasaran, & Ruang Lingkup

### 1.1 Pernyataan Masalah
Pengguna Indonesia yang belajar Bahasa Inggris sering menghadapi dua masalah utama:
1. **Materi tidak efektif** — terlalu panjang, abstrak, dan tidak langsung diikuti latihan.
2. **Bank soal terfragmentasi** — soal tersebar, tanpa pembahasan memadai, dan taksonomi tidak jelas.

Akibatnya, proses belajar tidak terstruktur, progress sulit diukur, dan motivasi cepat hilang.

### 1.2 Visi Produk
Membangun platform yang menggabungkan **buku digital interaktif** (materi ringkas, bilingual, common errors) dengan **bank soal Bahasa Inggris terkurasi** (lengkap pembahasan, metadata rapi), diperkuat dengan **review adaptif (SRS)**.

### 1.3 Prinsip Desain
- **Learning-first:** setiap konsep selalu diikuti latihan, umpan balik jelas, bilingual ID/EN.  
- **Structured-yet-flexible:** alur buku (materi → latihan → review), namun user bisa masuk lewat bank soal.  
- **Data-driven:** pakai telemetry untuk evaluasi kesulitan soal, misconception, progress mastery.  
- **Author-friendly:** CMS dengan validasi, preview, dan versioning.

### 1.4 Persona Utama
- **Learner (Siswa/Mahasiswa/Test-Prep):** butuh materi ringkas + latihan masif.  
- **Guru/Instruktur:** butuh soal siap pakai, bisa filter, dan export/assign.  
- **Author/Editor:** membuat & mereview materi/soal.  
- **Institution Admin (V3):** memonitor progres cohort/kelas.

### 1.5 Jobs To Be Done (JTBD)
- *Sebagai pelajar*, saya ingin membaca materi singkat dan contoh, lalu langsung berlatih agar cepat memahami dan mengingat.  
- *Sebagai peserta ujian*, saya ingin mengakses kumpulan soal sesuai level dan topik lengkap dengan pembahasan, agar bisa mengukur kesiapan saya.

### 1.6 Sasaran Keberhasilan (MVP)
- **North Star Metric:** jumlah *Mastered Items per Weekly Active Learner (WAL)*.  
- Retensi D7 ≥ 20%, D30 ≥ 8%.  
- Lesson completion rate ≥ 55%.  
- Review adherence (SRS done/day) ≥ 35%.  
- NPS ≥ 40.
- Mobile completion rate ≥ 70% (mengingat target user Indonesia).
- Time-to-first-question < 30 detik.
- Question load time p95 < 2 detik.

### 1.7 Ruang Lingkup
- **MVP:** Grammar + Vocabulary + Reading; materi ringkas; tipe soal (MCQ, Cloze, Ordering, Error Detect, Short Answer); Tryout sederhana; SRS dasar; CMS authoring; filter bank soal; dashboard progres sederhana; PWA dengan offline capability; gamification dasar (streaks, achievements).  
- **V2:** Listening, advanced analytics, social features, AI-powered personalization.
- **V3:** Speaking real-time, essay auto-grading, kelas institusional kompleks.
- **Non-Goal (MVP):** Real-time collaboration, advanced AI tutoring, institutional management.


### 1.8 Content Strategy & Prioritization
**Content Prioritization Matrix (MVP):**
- **Week 1-2:** Simple Present Tense (5 lessons + 50 soal)
- **Week 3-4:** Past Tense (5 lessons + 50 soal)  
- **Week 5-6:** Daily Vocabulary - Food, Family, Work (100 soal)
- **Week 7-8:** Question types diversification + Common Errors focus

**High-Impact Topics (A1-A2):**
- Basic tenses (Present, Past, Future)
- WH-questions dan Yes/No questions
- Common daily vocabulary (survival English)
- Prepositions of time and place
- Modal verbs (can, must, should)

### 1.9 Competitive Differentiation
**Key Differentiators vs Competitors:**
- **vs Duolingo:** Structured curriculum dengan pembahasan mendalam, bukan hanya gamification
- **vs Cake:** Focus pada grammar sistematis + bank soal comprehensive
- **vs ELSA:** Holistic approach (grammar + vocab + reading), bukan hanya pronunciation
- **Unique Value:** Bilingual explanations (ID/EN), Indonesian learner-specific common errors, bank soal dengan metadata lengkap

### 1.10 Monetization Strategy
**Freemium Model:**
- **Free Tier:** 3 lessons/hari, basic progress tracking, community features
- **Pro Tier (Rp 49k/bulan):** Unlimited lessons, advanced analytics, offline download, custom study plans, priority support
- **Institution Tier (V3):** Classroom management, bulk licensing, advanced reporting