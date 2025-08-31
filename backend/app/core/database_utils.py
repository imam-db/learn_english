"""
Database utility functions for common operations
"""

from typing import Optional, List, Dict, Any, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, Index
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select
import logging

from .database import AsyncSessionLocal
from ..models.base import Base

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Base)


class DatabaseUtils:
    """Utility class for common database operations"""
    
    @staticmethod
    async def create_indexes_if_not_exist(session: AsyncSession) -> None:
        """Create performance indexes if they don't exist"""
        try:
            # Full-text search indexes for lessons and questions (without CONCURRENTLY in transaction)
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_lessons_fts 
                ON lessons USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')))
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_questions_fts 
                ON questions USING gin(to_tsvector('english', stem || ' ' || COALESCE(explanation, '')))
            """))
            
            # Composite indexes for common queries
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_lesson_progress_user_completion 
                ON lesson_progress (user_id, is_completed, completion_percentage DESC)
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_question_attempts_user_performance 
                ON question_attempts (user_id, created_at DESC, is_correct)
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_srs_cards_review_queue 
                ON srs_cards (user_id, next_review_date, is_suspended) 
                WHERE is_suspended = false
            """))
            
            await session.commit()
            logger.info("Performance indexes created successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create indexes: {e}")
            # Don't raise the error, just log it as indexes are not critical for basic functionality
            logger.warning("Continuing without additional performance indexes")
    
    @staticmethod
    async def get_by_id(
        session: AsyncSession, 
        model: Type[T], 
        id: str,
        relationships: Optional[List[str]] = None
    ) -> Optional[T]:
        """Get a model instance by ID with optional relationship loading"""
        query = select(model).where(model.id == id)
        
        if relationships:
            for rel in relationships:
                query = query.options(selectinload(getattr(model, rel)))
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_field(
        session: AsyncSession,
        model: Type[T],
        field_name: str,
        field_value: Any,
        relationships: Optional[List[str]] = None
    ) -> Optional[T]:
        """Get a model instance by any field"""
        query = select(model).where(getattr(model, field_name) == field_value)
        
        if relationships:
            for rel in relationships:
                query = query.options(selectinload(getattr(model, rel)))
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_paginated(
        session: AsyncSession,
        query: Select,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ) -> Dict[str, Any]:
        """Get paginated results from a query"""
        # Validate pagination parameters
        page = max(1, page)
        per_page = min(max_per_page, max(1, per_page))
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        paginated_query = query.offset(offset).limit(per_page)
        result = await session.execute(paginated_query)
        items = result.scalars().all()
        
        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev,
                'next_page': page + 1 if has_next else None,
                'prev_page': page - 1 if has_prev else None
            }
        }
    
    @staticmethod
    async def bulk_create(
        session: AsyncSession,
        model: Type[T],
        data_list: List[Dict[str, Any]]
    ) -> List[T]:
        """Bulk create multiple instances"""
        instances = [model(**data) for data in data_list]
        session.add_all(instances)
        await session.flush()  # Get IDs without committing
        return instances
    
    @staticmethod
    async def bulk_update(
        session: AsyncSession,
        model: Type[T],
        updates: List[Dict[str, Any]]
    ) -> None:
        """Bulk update multiple instances"""
        if not updates:
            return
        
        # Group updates by model
        for update_data in updates:
            if 'id' not in update_data:
                raise ValueError("Each update must include an 'id' field")
            
            instance_id = update_data.pop('id')
            await session.execute(
                model.__table__.update()
                .where(model.id == instance_id)
                .values(**update_data)
            )
    
    @staticmethod
    async def soft_delete(
        session: AsyncSession,
        model: Type[T],
        id: str
    ) -> bool:
        """Soft delete by setting is_active = False (if model supports it)"""
        if not hasattr(model, 'is_active'):
            raise ValueError(f"Model {model.__name__} does not support soft delete")
        
        result = await session.execute(
            model.__table__.update()
            .where(model.id == id)
            .values(is_active=False)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def search_full_text(
        session: AsyncSession,
        model: Type[T],
        search_term: str,
        search_fields: List[str],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[T]:
        """Perform full-text search on specified fields"""
        # Build search vector from specified fields
        search_vector = func.to_tsvector(
            'english',
            func.concat(*[
                func.coalesce(getattr(model, field), '') + ' '
                for field in search_fields
            ])
        )
        
        # Build query with search ranking
        query = select(
            model,
            func.ts_rank(search_vector, func.plainto_tsquery('english', search_term)).label('rank')
        ).where(
            search_vector.op('@@')(func.plainto_tsquery('english', search_term))
        )
        
        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(model, field):
                    query = query.where(getattr(model, field) == value)
        
        # Order by relevance and limit results
        query = query.order_by(text('rank DESC')).limit(limit)
        
        result = await session.execute(query)
        return [row[0] for row in result.all()]  # Return only the model instances
    
    @staticmethod
    async def get_user_statistics(
        session: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        from ..models.progress import LessonProgress, QuestionAttempt
        from ..models.srs import SRSCard
        
        # Lesson progress stats
        lesson_stats = await session.execute(
            select(
                func.count(LessonProgress.id).label('total_lessons'),
                func.count(LessonProgress.id).filter(LessonProgress.is_completed == True).label('completed_lessons'),
                func.avg(LessonProgress.completion_percentage).label('avg_completion'),
                func.sum(LessonProgress.time_spent).label('total_time_spent')
            ).where(LessonProgress.user_id == user_id)
        )
        lesson_data = lesson_stats.first()
        
        # Question attempt stats
        question_stats = await session.execute(
            select(
                func.count(QuestionAttempt.id).label('total_attempts'),
                func.count(QuestionAttempt.id).filter(QuestionAttempt.is_correct == True).label('correct_attempts'),
                func.avg(QuestionAttempt.time_taken).label('avg_time_per_question')
            ).where(QuestionAttempt.user_id == user_id)
        )
        question_data = question_stats.first()
        
        # SRS stats
        srs_stats = await session.execute(
            select(
                func.count(SRSCard.id).label('total_cards'),
                func.count(SRSCard.id).filter(SRSCard.is_learning == False).label('mature_cards'),
                func.avg(SRSCard.ease_factor).label('avg_ease_factor')
            ).where(SRSCard.user_id == user_id)
        )
        srs_data = srs_stats.first()
        
        return {
            'lessons': {
                'total': lesson_data.total_lessons or 0,
                'completed': lesson_data.completed_lessons or 0,
                'avg_completion': float(lesson_data.avg_completion or 0),
                'total_time_spent': lesson_data.total_time_spent or 0
            },
            'questions': {
                'total_attempts': question_data.total_attempts or 0,
                'correct_attempts': question_data.correct_attempts or 0,
                'accuracy_rate': (
                    (question_data.correct_attempts / question_data.total_attempts * 100)
                    if question_data.total_attempts else 0
                ),
                'avg_time_per_question': float(question_data.avg_time_per_question or 0)
            },
            'srs': {
                'total_cards': srs_data.total_cards or 0,
                'mature_cards': srs_data.mature_cards or 0,
                'avg_ease_factor': float(srs_data.avg_ease_factor or 2.5)
            }
        }


# Convenience functions for common operations
async def get_db_session() -> AsyncSession:
    """Get a new database session"""
    return AsyncSessionLocal()


async def execute_with_retry(
    operation,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Any:
    """Execute database operation with retry logic"""
    import asyncio
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff