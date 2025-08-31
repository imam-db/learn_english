# PRD — Bank Soal + Buku Digital Bahasa Inggris (v1) — Bagian 3
**Tanggal:** 31 Agustus 2025  
**Penulis:** Imam × ChatGPT  
**Status:** Draft untuk MVP

---

# Bagian 3 — Bank Soal & Discovery

### 3.1 Taksonomi & Metadata Soal
- **Field pencarian:** stem, options, tags, topics, level, skill, difficulty, author.  
- **Facet/filter:** level (A1–C2), skill, topic, tipe soal, durasi estimasi, kesulitan.

### 3.2 Pencarian
**MVP Approach:**
- PostgreSQL FTS dengan aggressive caching (Redis)
- **Kinerja target:** p95 query < 400 ms untuk dataset 50k soal
- Cache strategy: 5 menit untuk popular queries

**Optimization Roadmap:**
- **V1.5:** Hybrid approach (PostgreSQL + Redis search cache)
- **V2:** ElasticSearch dengan advanced relevance scoring
- **V3:** AI-powered semantic search

**Search Performance Implementation:**
```python
class SearchService:
    async def search_questions(self, query, filters):
        cache_key = f"search:{hash(query)}:{hash(filters)}"
        cached = await self.redis.get(cache_key)
        if cached:
            return cached
        
        results = await self.db.fts_search(query, filters)
        await self.redis.setex(cache_key, 300, results)
        return results
```

**Ranking Algorithm:**
- Text relevance (40%)
- Question popularity/attempt count (30%)
- User success rate on similar questions (20%)
- Recency/freshness (10%)

### 3.3 Builder & Tryout
- **Custom Set:** user bisa pilih filter → tambah ke keranjang soal → simpan sebagai *Set*.  
- **Tryout Mode:** timer, no-feedback selama sesi, hasil & pembahasan setelah selesai.  
- **Practice Mode:** immediate feedback per soal.

### 3.4 Bookmark & Share
- User bisa simpan soal/lesson ke koleksi pribadi.  
- Tautan share publik (read-only) untuk soal/tryout.  
- V2: proteksi token/expiry untuk keamanan.

### 3.5 Contoh Alur User
1. User cari “Past Simple grammar B1” → hasil soal muncul dengan filter.  
2. User pilih 20 soal, simpan sebagai Set “Latihan UTS”.  
3. User jalankan Tryout dengan timer 30 menit.  
4. Setelah selesai, sistem tampilkan skor + pembahasan per soal.

### 3.6 Acceptance Criteria
- Pencarian & filter menghasilkan soal yang relevan dan cepat (p95 < 400ms).  
- User bisa menyusun & menjalankan Tryout dari bank soal.  
- Hasil tryout menampilkan skor total, waktu pengerjaan, dan pembahasan per soal.  
- User bisa bookmark soal atau set, dan membagikan lewat tautan publik.
- **Mobile optimization:** Touch-friendly interface untuk filter dan selection.
- **Offline support:** Downloaded question sets bisa diakses offline.
- **Performance monitoring:** Real-time tracking search response times.
- **A/B testing:** Framework untuk test different ranking algorithms.

### 3.7 Advanced Discovery Features (V2)
**AI-Powered Recommendations:**
- Similar questions based on topic/difficulty
- Personalized question suggestions based on learning history
- Weakness-targeted question sets
- Adaptive difficulty progression

**Social Discovery:**
- Community-created question sets
- Popular sets by skill level
- Peer-recommended content
- Study group shared collections

### 3.8 Performance Monitoring & Analytics
**Search Analytics:**
```json
{
  "search_metrics": {
    "query_response_time_p95": "< 400ms",
    "cache_hit_rate": "> 70%",
    "zero_results_rate": "< 5%",
    "click_through_rate": "> 60%"
  },
  "content_analytics": {
    "question_attempt_rate": "questions attempted vs shown",
    "completion_rate_by_difficulty": "success rate per difficulty level",
    "popular_search_terms": "trending topics/skills",
    "filter_usage_patterns": "most used filter combinations"
  }
}
```

**A/B Testing Framework:**
- Search ranking algorithm variations
- Filter UI/UX improvements
- Question presentation formats
- Tryout flow optimizations