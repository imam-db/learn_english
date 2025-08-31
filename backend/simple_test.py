#!/usr/bin/env python3
"""
Simple test to verify database models work correctly
"""

import asyncio
import uuid
from pathlib import Path
import sys

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.models.user import User, UserPreference
from app.models.content import Lesson, Question
from sqlalchemy import text


async def test_database_connection():
    """Test basic database connection"""
    print("Testing database connection...")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        print("✅ Database connection successful")


async def test_user_creation():
    """Test creating a user"""
    print("Testing user creation...")
    
    async with AsyncSessionLocal() as session:
        # Create unique email for test
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        user = User(
            email=test_email,
            password_hash="hashed_password",
            full_name="Test User",
            current_level="A1",
            is_active=True
        )
        session.add(user)
        await session.commit()
        
        print(f"✅ User created successfully: {user.email}")
        return user


async def test_lesson_creation():
    """Test creating a lesson"""
    print("Testing lesson creation...")
    
    async with AsyncSessionLocal() as session:
        lesson = Lesson(
            title="Test Lesson",
            slug=f"test-lesson-{uuid.uuid4().hex[:8]}",
            description="A test lesson",
            level="A1",
            skill="grammar",
            topic="test",
            difficulty=1,
            sections={"intro": {"content": "Test content"}},
            status="published"
        )
        session.add(lesson)
        await session.commit()
        
        print(f"✅ Lesson created successfully: {lesson.title}")
        return lesson


async def test_question_creation():
    """Test creating a question"""
    print("Testing question creation...")
    
    async with AsyncSessionLocal() as session:
        question = Question(
            stem="What is 2 + 2?",
            type="mcq",
            options={
                "A": {"text": "3"},
                "B": {"text": "4"},
                "C": {"text": "5"},
                "D": {"text": "6"}
            },
            answer_key=["B"],
            explanation="2 + 2 equals 4",
            level="A1",
            skill="grammar",
            topic="test",
            difficulty=1,
            points=1,
            status="published"
        )
        session.add(question)
        await session.commit()
        
        print(f"✅ Question created successfully: {question.stem}")
        return question


async def test_data_retrieval():
    """Test retrieving data from database"""
    print("Testing data retrieval...")
    
    async with AsyncSessionLocal() as session:
        # Count users
        user_count = await session.execute(text("SELECT COUNT(*) FROM users"))
        user_total = user_count.scalar()
        
        # Count lessons
        lesson_count = await session.execute(text("SELECT COUNT(*) FROM lessons"))
        lesson_total = lesson_count.scalar()
        
        # Count questions
        question_count = await session.execute(text("SELECT COUNT(*) FROM questions"))
        question_total = question_count.scalar()
        
        print(f"✅ Data retrieval successful:")
        print(f"   - Users: {user_total}")
        print(f"   - Lessons: {lesson_total}")
        print(f"   - Questions: {question_total}")


async def run_simple_tests():
    """Run all simple tests"""
    print("🚀 Starting simple database tests...\n")
    
    try:
        await test_database_connection()
        print()
        
        await test_user_creation()
        print()
        
        await test_lesson_creation()
        print()
        
        await test_question_creation()
        print()
        
        await test_data_retrieval()
        print()
        
        print("🎉 All simple tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_simple_tests())