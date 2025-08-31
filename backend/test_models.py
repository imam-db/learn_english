#!/usr/bin/env python3
"""
Test script to verify database models and relationships
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.models.user import User, UserPreference
from app.models.content import Lesson, Question, QuestionSet
from app.models.progress import LessonProgress, QuestionAttempt, UserAchievement
from app.models.srs import SRSCard
from app.models.assessment import TryoutSession, TryoutAnswer
from app.models.subscription import Subscription, PaymentTransaction


async def test_user_models():
    """Test user-related models"""
    print("Testing User models...")
    
    async with AsyncSessionLocal() as session:
        # Create a test user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            current_level="A2",
            learning_goals=["grammar", "vocabulary"],
            is_active=True,
            is_verified=True
        )
        session.add(user)
        await session.flush()
        
        # Create user preferences
        preferences = UserPreference(
            user_id=user.id,
            language_interface="id",
            daily_goal=5,
            reminder_enabled=True,
            offline_content_enabled=True
        )
        session.add(preferences)
        
        await session.commit()
        print(f"✅ Created user: {user.email} with ID: {user.id}")
        return user


async def test_content_models(user):
    """Test content-related models"""
    print("Testing Content models...")
    
    async with AsyncSessionLocal() as session:
        # Create a lesson
        lesson = Lesson(
            title="Test Lesson: Present Perfect",
            slug="test-present-perfect",
            description="Learn about present perfect tense",
            level="A2",
            skill="grammar",
            topic="tenses",
            difficulty=3,
            sections={
                "concept": {
                    "heading": "Present Perfect Tense",
                    "content": {
                        "en": "The present perfect tense connects past and present.",
                        "id": "Present perfect tense menghubungkan masa lalu dan sekarang."
                    }
                }
            },
            estimated_duration=20,
            status="published",
            author_id=user.id
        )
        session.add(lesson)
        await session.flush()
        
        # Create questions
        question1 = Question(
            stem="I _____ never _____ to Paris.",
            type="mcq",
            options={
                "A": {"text": "have / been", "explanation": {"en": "Correct!", "id": "Benar!"}},
                "B": {"text": "has / been", "explanation": {"en": "Wrong subject-verb agreement", "id": "Salah subjek-kata kerja"}},
                "C": {"text": "had / been", "explanation": {"en": "Wrong tense", "id": "Tense salah"}},
                "D": {"text": "am / been", "explanation": {"en": "Incorrect structure", "id": "Struktur salah"}}
            },
            answer_key=["A"],
            explanation="Present perfect uses 'have/has + past participle'",
            level="A2",
            skill="grammar",
            topic="tenses",
            difficulty=3,
            estimated_time=45,
            points=2,
            status="published",
            author_id=user.id
        )
        session.add(question1)
        
        question2 = Question(
            stem="She _____ her homework already.",
            type="mcq",
            options={
                "A": {"text": "finish", "explanation": {"en": "Wrong tense", "id": "Tense salah"}},
                "B": {"text": "finished", "explanation": {"en": "Simple past, not present perfect", "id": "Simple past, bukan present perfect"}},
                "C": {"text": "has finished", "explanation": {"en": "Correct!", "id": "Benar!"}},
                "D": {"text": "finishing", "explanation": {"en": "Wrong form", "id": "Bentuk salah"}}
            },
            answer_key=["C"],
            explanation="Present perfect with 'already' indicates completed action with present relevance",
            level="A2",
            skill="grammar",
            topic="tenses",
            difficulty=2,
            estimated_time=30,
            points=1,
            status="published",
            author_id=user.id
        )
        session.add(question2)
        await session.flush()
        
        # Create question set
        question_set = QuestionSet(
            title="Present Perfect Practice Set",
            description="Practice questions for present perfect tense",
            creator_id=user.id,
            is_public=True,
            time_limit=600,  # 10 minutes
            shuffle_questions=True,
            show_feedback="after_completion"
        )
        session.add(question_set)
        await session.flush()
        
        # Add questions to the set using association table
        from app.models.content import questionset_questions
        await session.execute(
            questionset_questions.insert().values([
                {"question_set_id": question_set.id, "question_id": question1.id, "order_index": 1},
                {"question_set_id": question_set.id, "question_id": question2.id, "order_index": 2}
            ])
        )
        
        await session.commit()
        print(f"✅ Created lesson: {lesson.title}")
        print(f"✅ Created {len([question1, question2])} questions")
        print(f"✅ Created question set: {question_set.title}")
        
        return lesson, [question1, question2], question_set


async def test_progress_models(user, lesson, questions):
    """Test progress tracking models"""
    print("Testing Progress models...")
    
    async with AsyncSessionLocal() as session:
        # Create lesson progress
        lesson_progress = LessonProgress(
            user_id=user.id,
            lesson_id=lesson.id,
            sections_completed=1,
            total_sections=3,
            completion_percentage=33.33,
            time_spent=300,  # 5 minutes
            questions_attempted=2,
            questions_correct=1,
            accuracy_rate=50.0,
            section_progress={"concept": True, "examples": False, "practice": False}
        )
        session.add(lesson_progress)
        
        # Create question attempts
        for i, question in enumerate(questions):
            attempt = QuestionAttempt(
                user_id=user.id,
                question_id=question.id,
                user_answer={"selected": "A" if i == 0 else "B"},  # First correct, second wrong
                is_correct=i == 0,
                time_taken=30 + i * 10,
                attempt_number=1,
                context_type="lesson",
                context_id=lesson.id,
                points_earned=question.points if i == 0 else 0,
                max_points=question.points
            )
            session.add(attempt)
        
        # Create achievement
        achievement = UserAchievement(
            user_id=user.id,
            achievement_type="completion",
            achievement_key="first_lesson",
            title="First Lesson Complete",
            description="Completed your first lesson",
            current_progress=1,
            target_progress=1,
            is_completed=True,
            category="learning",
            difficulty="bronze",
            points_reward=10,
            earned_at=datetime.utcnow().isoformat()
        )
        session.add(achievement)
        
        await session.commit()
        print(f"✅ Created lesson progress for user {user.email}")
        print(f"✅ Created {len(questions)} question attempts")
        print(f"✅ Created achievement: {achievement.title}")


async def test_srs_models(user, questions):
    """Test SRS models"""
    print("Testing SRS models...")
    
    async with AsyncSessionLocal() as session:
        # Create SRS cards for questions
        for question in questions:
            srs_card = SRSCard(
                user_id=user.id,
                item_type="question",
                item_id=question.id,
                question_id=question.id,
                interval=1,
                ease_factor=2.5,
                repetitions=0,
                next_review_date=(datetime.utcnow() + timedelta(days=1)).isoformat(),
                total_reviews=0,
                correct_reviews=0,
                consecutive_correct=0,
                is_learning=True,
                card_data={"difficulty_override": None}
            )
            session.add(srs_card)
        
        await session.commit()
        print(f"✅ Created {len(questions)} SRS cards")


async def test_assessment_models(user, question_set, questions):
    """Test assessment and tryout models"""
    print("Testing Assessment models...")
    
    async with AsyncSessionLocal() as session:
        # Create tryout session
        tryout_session = TryoutSession(
            user_id=user.id,
            question_set_id=question_set.id,
            title="Present Perfect Tryout",
            time_limit=600,
            total_questions=len(questions),
            status="completed",
            current_question_index=len(questions),
            started_at=datetime.utcnow().isoformat(),
            completed_at=(datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            time_elapsed=300,
            questions_answered=len(questions),
            correct_answers=1,
            total_points=1,
            max_possible_points=3,
            accuracy_percentage=33.33,
            average_time_per_question=150,
            question_order=[str(q.id) for q in questions]
        )
        session.add(tryout_session)
        await session.flush()
        
        # Create tryout answers
        for i, question in enumerate(questions):
            answer = TryoutAnswer(
                session_id=tryout_session.id,
                question_id=question.id,
                user_answer={"selected": "A" if i == 0 else "B"},
                is_correct=i == 0,
                points_earned=question.points if i == 0 else 0,
                max_points=question.points,
                time_taken=120 + i * 60,
                answered_at=(datetime.utcnow() + timedelta(minutes=i)).isoformat(),
                question_index=i
            )
            session.add(answer)
        
        await session.commit()
        print(f"✅ Created tryout session: {tryout_session.title}")
        print(f"✅ Created {len(questions)} tryout answers")


async def test_subscription_models(user):
    """Test subscription and payment models"""
    print("Testing Subscription models...")
    
    async with AsyncSessionLocal() as session:
        # Create subscription
        subscription = Subscription(
            user_id=user.id,
            plan_type="pro",
            status="active",
            billing_cycle="monthly",
            price=49000,  # IDR 49,000
            currency="IDR",
            started_at=datetime.utcnow().isoformat(),
            current_period_start=datetime.utcnow().isoformat(),
            current_period_end=(datetime.utcnow() + timedelta(days=30)).isoformat(),
            daily_lessons_used=3,
            last_usage_reset=datetime.utcnow().date().isoformat()
        )
        session.add(subscription)
        await session.flush()
        
        # Create payment transaction
        transaction = PaymentTransaction(
            subscription_id=subscription.id,
            user_id=user.id,
            transaction_type="subscription",
            status="completed",
            amount=49000,
            currency="IDR",
            payment_method="gopay",
            gateway="midtrans",
            external_transaction_id="TXN_123456789",
            initiated_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat(),
            billing_period_start=subscription.current_period_start,
            billing_period_end=subscription.current_period_end,
            description="Monthly Pro subscription"
        )
        session.add(transaction)
        
        await session.commit()
        print(f"✅ Created subscription: {subscription.plan_type}")
        print(f"✅ Created payment transaction: {transaction.external_transaction_id}")


async def run_all_tests():
    """Run all model tests"""
    print("🚀 Starting database model tests...\n")
    
    try:
        # Test user models
        user = await test_user_models()
        print()
        
        # Test content models
        lesson, questions, question_set = await test_content_models(user)
        print()
        
        # Test progress models
        await test_progress_models(user, lesson, questions)
        print()
        
        # Test SRS models
        await test_srs_models(user, questions)
        print()
        
        # Test assessment models
        await test_assessment_models(user, question_set, questions)
        print()
        
        # Test subscription models
        await test_subscription_models(user)
        print()
        
        print("🎉 All model tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())