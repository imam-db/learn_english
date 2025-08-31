# Database Schema and Models Implementation

This document describes the database schema and models implementation for the English Learning Platform.

## Overview

The database is implemented using:
- **PostgreSQL 15+** as the primary database
- **SQLAlchemy 2.0** with async support for ORM
- **Alembic** for database migrations
- **asyncpg** for async PostgreSQL driver
- **Redis** for caching and sessions

## Database Models

### Core Models

#### 1. User Management
- **`users`** - User accounts and authentication
- **`user_preferences`** - User settings and preferences

#### 2. Content Management
- **`lessons`** - Interactive lesson content
- **`questions`** - Question bank with multiple types
- **`question_sets`** - Custom collections of questions

#### 3. Progress Tracking
- **`lesson_progress`** - User progress through lessons
- **`question_attempts`** - Individual question attempt records
- **`user_achievements`** - Badges and achievements

#### 4. Spaced Repetition System (SRS)
- **`srs_cards`** - SRS cards for spaced repetition learning

#### 5. Assessment System
- **`tryout_sessions`** - Timed assessment sessions
- **`tryout_answers`** - Individual answers within tryout sessions

#### 6. Subscription Management
- **`subscriptions`** - User subscription records
- **`payment_transactions`** - Payment transaction history

### Association Tables
- **`lesson_questions`** - Many-to-many relationship between lessons and questions
- **`questionset_questions`** - Many-to-many relationship between question sets and questions

## Key Features

### 1. Flexible Content Structure
- **JSONB fields** for flexible lesson sections and question options
- **Bilingual support** with Indonesian and English content
- **Hierarchical content** organization (Path → Unit → Lesson → Section)

### 2. Performance Optimization
- **Comprehensive indexing** for search and filtering operations
- **Full-text search** using PostgreSQL's built-in FTS
- **Connection pooling** with configurable pool sizes
- **Query optimization** with proper relationship loading

### 3. Data Integrity
- **Check constraints** for data validation
- **Foreign key constraints** with proper cascade rules
- **Unique constraints** for business logic enforcement
- **NOT NULL constraints** for required fields

### 4. Scalability Features
- **UUID primary keys** for distributed systems
- **Async database operations** for high concurrency
- **Pagination support** with efficient offset/limit queries
- **Bulk operations** for data import/export

## Database Schema Highlights

### User Model
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    current_level VARCHAR(10) DEFAULT 'A1',
    learning_goals TEXT[],
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_premium BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Lesson Model
```sql
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    level VARCHAR(10) NOT NULL,
    skill VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    sections JSONB NOT NULL,  -- Flexible lesson structure
    status VARCHAR(20) DEFAULT 'draft',
    search_vector TSVECTOR,   -- Full-text search
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Question Model
```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stem TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    options JSONB,            -- Flexible question options
    answer_key JSONB NOT NULL,
    explanation TEXT,
    level VARCHAR(10) NOT NULL,
    skill VARCHAR(50) NOT NULL,
    difficulty INTEGER DEFAULT 3,
    search_vector TSVECTOR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### SRS Card Model
```sql
CREATE TABLE srs_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    item_type VARCHAR(50) NOT NULL,
    item_id UUID NOT NULL,
    interval INTEGER DEFAULT 1,
    ease_factor DECIMAL(4,2) DEFAULT 2.5,
    repetitions INTEGER DEFAULT 0,
    next_review_date VARCHAR NOT NULL,
    is_learning BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Indexes and Performance

### Primary Indexes
- All tables have UUID primary keys with indexes
- Unique indexes on email, slug, and other unique fields
- Foreign key indexes for relationship queries

### Search Indexes
- Full-text search indexes on lessons and questions using GIN
- Composite indexes for common query patterns
- Partial indexes for filtered queries (e.g., active users only)

### Performance Indexes
```sql
-- Lesson search and filtering
CREATE INDEX idx_lessons_level_skill ON lessons (level, skill);
CREATE INDEX idx_lessons_search ON lessons USING gin(search_vector);

-- Question search and filtering  
CREATE INDEX idx_questions_type_level ON questions (type, level);
CREATE INDEX idx_questions_search ON questions USING gin(search_vector);

-- SRS review queue optimization
CREATE INDEX idx_srs_cards_due ON srs_cards (user_id, next_review_date);

-- Progress tracking
CREATE INDEX idx_lesson_progress_completion ON lesson_progress (user_id, completion_percentage);
```

## Data Validation

### Check Constraints
- CEFR level validation: `level IN ('A1', 'A2', 'B1', 'B2')`
- Skill type validation: `skill IN ('grammar', 'vocabulary', 'reading', ...)`
- Difficulty range: `difficulty >= 1 AND difficulty <= 5`
- Percentage validation: `completion_percentage >= 0 AND completion_percentage <= 100`

### Business Logic Constraints
- Questions correct ≤ questions attempted
- SRS ease factor within valid range (1.3 - 5.0)
- Payment amounts must be positive
- Subscription dates must be logical

## Migration Management

### Alembic Setup
- Migration files in `backend/alembic/versions/`
- Environment configuration in `backend/alembic/env.py`
- Auto-generation support for model changes

### Migration Commands
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Database Utilities

### Connection Management
- Async connection pooling with configurable sizes
- Health check endpoints for monitoring
- Graceful connection handling with retries

### Common Operations
- Pagination utilities for large datasets
- Bulk operations for data import/export
- Full-text search helpers
- User statistics aggregation

### Development Tools
- Database initialization script (`manage_db.py`)
- Model testing script (`test_models.py`)
- Seed data for development environment

## Usage Examples

### Basic Model Usage
```python
from app.models.user import User
from app.core.database import get_db

async def create_user(db: AsyncSession):
    user = User(
        email="user@example.com",
        password_hash="hashed_password",
        full_name="John Doe",
        current_level="A1"
    )
    db.add(user)
    await db.commit()
    return user
```

### Search and Filtering
```python
from app.core.database_utils import DatabaseUtils

# Full-text search
results = await DatabaseUtils.search_full_text(
    session=db,
    model=Question,
    search_term="present perfect",
    search_fields=["stem", "explanation"],
    filters={"level": "A2"},
    limit=20
)

# Paginated results
paginated = await DatabaseUtils.get_paginated(
    session=db,
    query=select(Lesson).where(Lesson.level == "A1"),
    page=1,
    per_page=10
)
```

### SRS Operations
```python
from app.models.srs import SRSCard

# Get due reviews
due_cards = await session.execute(
    select(SRSCard)
    .where(SRSCard.user_id == user_id)
    .where(SRSCard.next_review_date <= today)
    .where(SRSCard.is_suspended == False)
)
```

## Environment Configuration

### Database Settings
```python
# In app/core/config.py
DATABASE_URL = "postgresql://user:pass@localhost:5432/db_name"
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
```

### Connection String Format
```
postgresql+asyncpg://username:password@host:port/database_name
```

## Monitoring and Maintenance

### Health Checks
- Database connection health endpoint
- Query performance monitoring
- Connection pool status

### Backup Strategy
- Regular automated backups
- Point-in-time recovery capability
- Migration rollback procedures

### Performance Monitoring
- Query execution time tracking
- Index usage analysis
- Connection pool metrics

## Security Considerations

### Data Protection
- Password hashing with bcrypt
- Sensitive data encryption
- SQL injection prevention with parameterized queries

### Access Control
- Role-based access control (RBAC)
- User session management
- API rate limiting

### Audit Trail
- Created/updated timestamps on all records
- User action tracking through question attempts
- Payment transaction logging

This database implementation provides a solid foundation for the English Learning Platform with excellent performance, scalability, and maintainability characteristics.