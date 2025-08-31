# PRD — Bank Soal + Buku Digital Bahasa Inggris (v1) — Bagian 4
**Tanggal:** 31 Agustus 2025  
**Penulis:** Imam × ChatGPT  
**Status:** Draft untuk MVP

---

# Bagian 4 — CMS Author/Admin

### 4.1 Peran & RBAC
- **Author:** buat/edit konten.  
- **Reviewer/Editor:** review, minta revisi.  
- **Publisher:** publish/unpublish, schedule konten.  
- **Admin:** semua hak + manajemen user/role + konfigurasi tag/taksonomi.

### 4.2 Alur Kerja Konten
- Workflow: Draft → Review → Approved → Published.  
- Komentar inline pada stem/opsi/section.  
- Versioning: `v1.0`, `v1.1` (patch), riwayat perubahan tersimpan.

### 4.3 Fitur Authoring
- Editor WYSIWYG untuk **sections** (Concept, Examples, Common Errors).  
- Form builder untuk **Question** (MCQ, Cloze, Ordering, Error, Short Answer).  
- **Preview:** lesson/soal sebelum publish.  
- **Bulk Import:** CSV/JSON/Excel → validasi otomatis → laporan error.  
- **Content Linting:** cek field wajib, ejaan, duplikasi, konsistensi level/tag.

### 4.4 Publishing & Lifecycle
- Jadwal publish otomatis (scheduled content).  
- Deprecate/retire konten lama, dengan redirect mapping (lesson lama ke baru).  
- Tagging konsisten melalui kamus tag.  
- Aset media (gambar/audio) disimpan via CDN dengan optimasi ukuran.

### 4.5 Acceptance Criteria
- Author dapat membuat 1 lesson + 10 soal via UI dan publish.  
- Reviewer dapat memberi komentar & approve.  
- Publisher dapat menjadwalkan publish dan menarik konten.  
- Import 100 soal dari CSV lewat UI dengan validasi sukses.  
- Semua role (Author, Reviewer, Publisher, Admin) bisa diatur via RBAC dan diuji fungsinya.
- **Content validation:** Automated linting pipeline dengan 95% accuracy.
- **Performance:** Content creation workflow < 5 menit untuk 1 lesson.
- **Quality assurance:** Native speaker validation integration.
- **Analytics integration:** Content performance tracking dari CMS.

### 4.6 Advanced Content Validation
**Automated Content Linting Pipeline:**
```python
class ContentValidator:
    def validate_lesson(self, lesson):
        validation_results = {
            'required_fields': self.check_required_fields(lesson),
            'grammar_consistency': self.check_grammar_rules(lesson),
            'difficulty_alignment': self.check_cefr_alignment(lesson),
            'bilingual_accuracy': self.check_translation_quality(lesson),
            'cultural_relevance': self.check_indonesian_context(lesson),
            'common_errors_authenticity': self.validate_error_examples(lesson)
        }
        return validation_results

    def generate_improvement_suggestions(self, validation_results):
        # AI-powered suggestions untuk content improvement
        pass
```

**Quality Assurance Workflow:**
1. **Automated Validation:** Grammar, consistency, alignment checks
2. **Peer Review:** Author → Reviewer feedback loop
3. **Native Speaker Validation:** Critical content review
4. **A/B Testing:** Content effectiveness measurement
5. **Continuous Improvement:** Performance-based content updates

### 4.7 Content Performance Analytics
**CMS Analytics Dashboard:**
- Content creation velocity (lessons/week per author)
- Review cycle time (draft → published)
- Content quality scores (validation pass rates)
- User engagement per content piece
- Error detection accuracy rates

**Content Effectiveness Metrics:**
```json
{
  "lesson_metrics": {
    "completion_rate": "% users who finish lesson",
    "time_to_complete": "average completion time",
    "concept_mastery_rate": "% achieving 80%+ accuracy",
    "retention_impact": "D7 retention for users who completed"
  },
  "question_metrics": {
    "difficulty_accuracy": "empirical vs intended difficulty",
    "discrimination_index": "ability to differentiate skill levels",
    "distractor_effectiveness": "wrong answer selection patterns",
    "time_to_answer": "average response time"
  }
}
```

### 4.8 Scalability & Automation
**Content Scaling Strategy:**
- **Template-based creation:** Standardized lesson templates
- **AI-assisted generation:** Question variations from base content
- **Community contributions:** Curated user-generated content
- **Automated translations:** ID/EN with human review
- **Bulk operations:** Mass content updates and migrations