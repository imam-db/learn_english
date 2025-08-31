"""Initial database schema with all core models

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-08-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('current_level', sa.String(length=10), nullable=False),
        sa.Column('learning_goals', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('is_premium', sa.Boolean(), nullable=False),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('reset_password_token', sa.String(length=255), nullable=True),
        sa.CheckConstraint("current_level IN ('A1', 'A2', 'B1', 'B2')", name='valid_cefr_level'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email_active', 'users', ['email', 'is_active'], unique=False)
    op.create_index('idx_users_level', 'users', ['current_level'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('language_interface', sa.String(length=10), nullable=False),
        sa.Column('theme', sa.String(length=20), nullable=False),
        sa.Column('daily_goal', sa.Integer(), nullable=False),
        sa.Column('reminder_enabled', sa.Boolean(), nullable=False),
        sa.Column('reminder_time', sa.String(length=5), nullable=False),
        sa.Column('offline_content_enabled', sa.Boolean(), nullable=False),
        sa.Column('auto_play_audio', sa.Boolean(), nullable=False),
        sa.Column('show_translations', sa.Boolean(), nullable=False),
        sa.Column('email_notifications', sa.Boolean(), nullable=False),
        sa.Column('push_notifications', sa.Boolean(), nullable=False),
        sa.CheckConstraint("language_interface IN ('id', 'en')", name='valid_interface_language'),
        sa.CheckConstraint("theme IN ('light', 'dark', 'auto')", name='valid_theme'),
        sa.CheckConstraint('daily_goal > 0 AND daily_goal <= 50', name='valid_daily_goal'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_id'), 'user_preferences', ['id'], unique=False)

    # Create lessons table
    op.create_table('lessons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('level', sa.String(length=10), nullable=False),
        sa.Column('skill', sa.String(length=50), nullable=False),
        sa.Column('topic', sa.String(length=100), nullable=False),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('sections', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('prerequisites', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_objectives', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('published_at', sa.String(), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('completion_count', sa.Integer(), nullable=False),
        sa.Column('average_rating', sa.Integer(), nullable=True),
        sa.CheckConstraint("level IN ('A1', 'A2', 'B1', 'B2')", name='valid_lesson_level'),
        sa.CheckConstraint("skill IN ('grammar', 'vocabulary', 'reading', 'listening', 'writing', 'speaking')", name='valid_skill_type'),
        sa.CheckConstraint('difficulty >= 1 AND difficulty <= 5', name='valid_difficulty_range'),
        sa.CheckConstraint("status IN ('draft', 'review', 'published', 'archived')", name='valid_lesson_status'),
        sa.CheckConstraint('estimated_duration > 0 AND estimated_duration <= 120', name='valid_duration_range'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_lessons_level_skill', 'lessons', ['level', 'skill'], unique=False)
    op.create_index('idx_lessons_topic_difficulty', 'lessons', ['topic', 'difficulty'], unique=False)
    op.create_index('idx_lessons_status_published', 'lessons', ['status', 'published_at'], unique=False)
    op.create_index('idx_lessons_search', 'lessons', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_lessons_id'), 'lessons', ['id'], unique=False)
    op.create_index(op.f('ix_lessons_level'), 'lessons', ['level'], unique=False)
    op.create_index(op.f('ix_lessons_skill'), 'lessons', ['skill'], unique=False)
    op.create_index(op.f('ix_lessons_slug'), 'lessons', ['slug'], unique=False)
    op.create_index(op.f('ix_lessons_topic'), 'lessons', ['topic'], unique=False)

    # Create questions table
    op.create_table('questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('stem', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('answer_key', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('level', sa.String(length=10), nullable=False),
        sa.Column('skill', sa.String(length=50), nullable=False),
        sa.Column('topic', sa.String(length=100), nullable=False),
        sa.Column('subtopic', sa.String(length=100), nullable=True),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('estimated_time', sa.Integer(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('hints', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('attempt_count', sa.Integer(), nullable=False),
        sa.Column('correct_count', sa.Integer(), nullable=False),
        sa.Column('average_time', sa.Integer(), nullable=True),
        sa.CheckConstraint("type IN ('mcq', 'cloze', 'ordering', 'error_detection', 'short_answer', 'matching', 'true_false')", name='valid_question_type'),
        sa.CheckConstraint("level IN ('A1', 'A2', 'B1', 'B2')", name='valid_question_level'),
        sa.CheckConstraint("skill IN ('grammar', 'vocabulary', 'reading', 'listening', 'writing', 'speaking')", name='valid_question_skill'),
        sa.CheckConstraint('difficulty >= 1 AND difficulty <= 5', name='valid_question_difficulty'),
        sa.CheckConstraint("status IN ('draft', 'review', 'published', 'archived')", name='valid_question_status'),
        sa.CheckConstraint('points > 0 AND points <= 10', name='valid_points_range'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_questions_type_level', 'questions', ['type', 'level'], unique=False)
    op.create_index('idx_questions_skill_topic', 'questions', ['skill', 'topic'], unique=False)
    op.create_index('idx_questions_difficulty_status', 'questions', ['difficulty', 'status'], unique=False)
    op.create_index('idx_questions_search', 'questions', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_index(op.f('ix_questions_level'), 'questions', ['level'], unique=False)
    op.create_index(op.f('ix_questions_skill'), 'questions', ['skill'], unique=False)
    op.create_index(op.f('ix_questions_topic'), 'questions', ['topic'], unique=False)
    op.create_index(op.f('ix_questions_type'), 'questions', ['type'], unique=False)

    # Create question_sets table
    op.create_table('question_sets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('is_official', sa.Boolean(), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('shuffle_questions', sa.Boolean(), nullable=False),
        sa.Column('shuffle_options', sa.Boolean(), nullable=False),
        sa.Column('show_feedback', sa.String(length=20), nullable=False),
        sa.Column('filter_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_dynamic', sa.Boolean(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('average_score', sa.Integer(), nullable=True),
        sa.CheckConstraint("show_feedback IN ('immediate', 'after_question', 'after_completion', 'never')", name='valid_feedback_mode'),
        sa.CheckConstraint('time_limit IS NULL OR time_limit > 0', name='valid_time_limit'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_question_sets_creator', 'question_sets', ['creator_id'], unique=False)
    op.create_index('idx_question_sets_public_official', 'question_sets', ['is_public', 'is_official'], unique=False)
    op.create_index(op.f('ix_question_sets_id'), 'question_sets', ['id'], unique=False)

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('started_at', sa.String(), nullable=False),
        sa.Column('current_period_start', sa.String(), nullable=False),
        sa.Column('current_period_end', sa.String(), nullable=False),
        sa.Column('canceled_at', sa.String(), nullable=True),
        sa.Column('ended_at', sa.String(), nullable=True),
        sa.Column('trial_start', sa.String(), nullable=True),
        sa.Column('trial_end', sa.String(), nullable=True),
        sa.Column('is_trial', sa.Boolean(), nullable=False),
        sa.Column('external_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('daily_lessons_used', sa.Integer(), nullable=False),
        sa.Column('last_usage_reset', sa.String(), nullable=True),
        sa.Column('subscription_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint("plan_type IN ('free', 'pro', 'premium', 'enterprise')", name='valid_plan_type'),
        sa.CheckConstraint("status IN ('active', 'canceled', 'expired', 'suspended', 'pending')", name='valid_subscription_status'),
        sa.CheckConstraint("billing_cycle IN ('monthly', 'yearly', 'lifetime') OR billing_cycle IS NULL", name='valid_billing_cycle'),
        sa.CheckConstraint("currency IN ('IDR', 'USD')", name='valid_currency'),
        sa.CheckConstraint('price >= 0', name='valid_price'),
        sa.CheckConstraint('daily_lessons_used >= 0', name='valid_daily_usage'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_subscriptions_user', 'subscriptions', ['user_id'], unique=False)
    op.create_index('idx_subscriptions_status', 'subscriptions', ['status'], unique=False)
    op.create_index('idx_subscriptions_plan', 'subscriptions', ['plan_type'], unique=False)
    op.create_index('idx_subscriptions_external', 'subscriptions', ['external_subscription_id'], unique=False)
    op.create_index('idx_subscriptions_period', 'subscriptions', ['current_period_start', 'current_period_end'], unique=False)
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)

    # Create lesson_questions association table
    op.create_table('lesson_questions',
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('section_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE')
    )
    op.create_index('idx_lesson_questions_lesson', 'lesson_questions', ['lesson_id'], unique=False)
    op.create_index('idx_lesson_questions_question', 'lesson_questions', ['question_id'], unique=False)

    # Create lesson_progress table
    op.create_table('lesson_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sections_completed', sa.Integer(), nullable=False),
        sa.Column('total_sections', sa.Integer(), nullable=False),
        sa.Column('completion_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('time_spent', sa.Integer(), nullable=False),
        sa.Column('first_started_at', sa.String(), nullable=True),
        sa.Column('last_accessed_at', sa.String(), nullable=True),
        sa.Column('completed_at', sa.String(), nullable=True),
        sa.Column('questions_attempted', sa.Integer(), nullable=False),
        sa.Column('questions_correct', sa.Integer(), nullable=False),
        sa.Column('accuracy_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('section_progress', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('is_bookmarked', sa.Boolean(), nullable=False),
        sa.CheckConstraint('completion_percentage >= 0 AND completion_percentage <= 100', name='valid_completion_percentage'),
        sa.CheckConstraint('accuracy_rate >= 0 AND accuracy_rate <= 100', name='valid_accuracy_rate'),
        sa.CheckConstraint('sections_completed >= 0 AND sections_completed <= total_sections', name='valid_sections_completed'),
        sa.CheckConstraint('questions_correct <= questions_attempted', name='valid_questions_correct'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson_progress')
    )
    op.create_index('idx_lesson_progress_user', 'lesson_progress', ['user_id'], unique=False)
    op.create_index('idx_lesson_progress_lesson', 'lesson_progress', ['lesson_id'], unique=False)
    op.create_index('idx_lesson_progress_completion', 'lesson_progress', ['user_id', 'completion_percentage'], unique=False)
    op.create_index('idx_lesson_progress_bookmarked', 'lesson_progress', ['user_id', 'is_bookmarked'], unique=False)
    op.create_index(op.f('ix_lesson_progress_id'), 'lesson_progress', ['id'], unique=False)

    # Create payment_transactions table
    op.create_table('payment_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('gateway', sa.String(length=50), nullable=False),
        sa.Column('external_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('gateway_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('initiated_at', sa.String(), nullable=False),
        sa.Column('completed_at', sa.String(), nullable=True),
        sa.Column('failed_at', sa.String(), nullable=True),
        sa.Column('billing_period_start', sa.String(), nullable=True),
        sa.Column('billing_period_end', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('invoice_number', sa.String(length=100), nullable=True),
        sa.Column('receipt_url', sa.String(length=500), nullable=True),
        sa.Column('refunded_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('refunded_at', sa.String(), nullable=True),
        sa.Column('refund_reason', sa.Text(), nullable=True),
        sa.CheckConstraint("transaction_type IN ('subscription', 'upgrade', 'renewal', 'refund', 'chargeback')", name='valid_transaction_type'),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed', 'canceled', 'refunded')", name='valid_transaction_status'),
        sa.CheckConstraint("gateway IN ('midtrans', 'gopay', 'ovo', 'dana', 'bank_transfer', 'credit_card')", name='valid_payment_gateway'),
        sa.CheckConstraint('amount > 0', name='valid_transaction_amount'),
        sa.CheckConstraint('refunded_amount >= 0 AND refunded_amount <= amount', name='valid_refunded_amount'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_payment_transactions_subscription', 'payment_transactions', ['subscription_id'], unique=False)
    op.create_index('idx_payment_transactions_user', 'payment_transactions', ['user_id'], unique=False)
    op.create_index('idx_payment_transactions_status', 'payment_transactions', ['status'], unique=False)
    op.create_index('idx_payment_transactions_external', 'payment_transactions', ['external_transaction_id'], unique=False)
    op.create_index('idx_payment_transactions_gateway', 'payment_transactions', ['gateway'], unique=False)
    op.create_index('idx_payment_transactions_date', 'payment_transactions', ['initiated_at'], unique=False)
    op.create_index(op.f('ix_payment_transactions_id'), 'payment_transactions', ['id'], unique=False)

    # Create question_attempts table
    op.create_table('question_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_answer', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('time_taken', sa.Integer(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('context_type', sa.String(length=50), nullable=True),
        sa.Column('context_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False),
        sa.Column('max_points', sa.Integer(), nullable=False),
        sa.Column('hint_used', sa.Boolean(), nullable=False),
        sa.Column('explanation_viewed', sa.Boolean(), nullable=False),
        sa.CheckConstraint("context_type IN ('lesson', 'practice', 'tryout', 'srs', 'assessment')", name='valid_context_type'),
        sa.CheckConstraint('attempt_number > 0', name='valid_attempt_number'),
        sa.CheckConstraint('time_taken > 0', name='valid_time_taken'),
        sa.CheckConstraint('points_earned >= 0 AND points_earned <= max_points', name='valid_points_earned'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_question_attempts_user', 'question_attempts', ['user_id'], unique=False)
    op.create_index('idx_question_attempts_question', 'question_attempts', ['question_id'], unique=False)
    op.create_index('idx_question_attempts_context', 'question_attempts', ['context_type', 'context_id'], unique=False)
    op.create_index('idx_question_attempts_user_question', 'question_attempts', ['user_id', 'question_id'], unique=False)
    op.create_index('idx_question_attempts_performance', 'question_attempts', ['user_id', 'is_correct', 'created_at'], unique=False)
    op.create_index(op.f('ix_question_attempts_id'), 'question_attempts', ['id'], unique=False)

    # Create questionset_questions association table
    op.create_table('questionset_questions',
        sa.Column('question_set_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_set_id'], ['question_sets.id'], ondelete='CASCADE')
    )
    op.create_index('idx_questionset_questions_set', 'questionset_questions', ['question_set_id'], unique=False)
    op.create_index('idx_questionset_questions_question', 'questionset_questions', ['question_id'], unique=False)

    # Create srs_cards table
    op.create_table('srs_cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_type', sa.String(length=50), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('interval', sa.Integer(), nullable=False),
        sa.Column('ease_factor', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('repetitions', sa.Integer(), nullable=False),
        sa.Column('next_review_date', sa.String(), nullable=False),
        sa.Column('last_reviewed_date', sa.String(), nullable=True),
        sa.Column('total_reviews', sa.Integer(), nullable=False),
        sa.Column('correct_reviews', sa.Integer(), nullable=False),
        sa.Column('consecutive_correct', sa.Integer(), nullable=False),
        sa.Column('is_learning', sa.Boolean(), nullable=False),
        sa.Column('is_suspended', sa.Boolean(), nullable=False),
        sa.Column('is_buried', sa.Boolean(), nullable=False),
        sa.Column('card_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('average_response_time', sa.Integer(), nullable=True),
        sa.Column('difficulty_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.CheckConstraint("item_type IN ('question', 'vocabulary', 'grammar_rule', 'phrase', 'concept')", name='valid_srs_item_type'),
        sa.CheckConstraint('interval > 0', name='valid_srs_interval'),
        sa.CheckConstraint('ease_factor >= 1.3 AND ease_factor <= 5.0', name='valid_ease_factor'),
        sa.CheckConstraint('repetitions >= 0', name='valid_repetitions'),
        sa.CheckConstraint('correct_reviews <= total_reviews', name='valid_correct_reviews'),
        sa.CheckConstraint('consecutive_correct >= 0', name='valid_consecutive_correct'),
        sa.CheckConstraint('difficulty_rating >= 0 AND difficulty_rating <= 5', name='valid_difficulty_rating'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_srs_cards_user', 'srs_cards', ['user_id'], unique=False)
    op.create_index('idx_srs_cards_item', 'srs_cards', ['item_type', 'item_id'], unique=False)
    op.create_index('idx_srs_cards_question', 'srs_cards', ['question_id'], unique=False)
    op.create_index('idx_srs_cards_due', 'srs_cards', ['user_id', 'next_review_date'], unique=False)
    op.create_index('idx_srs_cards_learning', 'srs_cards', ['user_id', 'is_learning'], unique=False)
    op.create_index('idx_srs_cards_suspended', 'srs_cards', ['user_id', 'is_suspended'], unique=False)
    op.create_index(op.f('ix_srs_cards_id'), 'srs_cards', ['id'], unique=False)

    # Create tryout_sessions table
    op.create_table('tryout_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_set_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('current_question_index', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.String(), nullable=True),
        sa.Column('completed_at', sa.String(), nullable=True),
        sa.Column('time_elapsed', sa.Integer(), nullable=False),
        sa.Column('time_remaining', sa.Integer(), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=False),
        sa.Column('correct_answers', sa.Integer(), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=False),
        sa.Column('max_possible_points', sa.Integer(), nullable=False),
        sa.Column('accuracy_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('average_time_per_question', sa.Integer(), nullable=True),
        sa.Column('shuffle_questions', sa.Boolean(), nullable=False),
        sa.Column('shuffle_options', sa.Boolean(), nullable=False),
        sa.Column('show_feedback', sa.String(length=20), nullable=False),
        sa.Column('question_order', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('session_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint("status IN ('not_started', 'in_progress', 'paused', 'completed', 'abandoned')", name='valid_session_status'),
        sa.CheckConstraint("show_feedback IN ('immediate', 'after_question', 'after_completion', 'never')", name='valid_feedback_mode'),
        sa.CheckConstraint('current_question_index >= 0 AND current_question_index <= total_questions', name='valid_question_index'),
        sa.CheckConstraint('questions_answered >= 0 AND questions_answered <= total_questions', name='valid_questions_answered'),
        sa.CheckConstraint('correct_answers >= 0 AND correct_answers <= questions_answered', name='valid_correct_answers'),
        sa.CheckConstraint('accuracy_percentage >= 0 AND accuracy_percentage <= 100', name='valid_accuracy_percentage'),
        sa.ForeignKeyConstraint(['question_set_id'], ['question_sets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tryout_sessions_user', 'tryout_sessions', ['user_id'], unique=False)
    op.create_index('idx_tryout_sessions_question_set', 'tryout_sessions', ['question_set_id'], unique=False)
    op.create_index('idx_tryout_sessions_status', 'tryout_sessions', ['user_id', 'status'], unique=False)
    op.create_index('idx_tryout_sessions_completed', 'tryout_sessions', ['user_id', 'completed_at'], unique=False)
    op.create_index(op.f('ix_tryout_sessions_id'), 'tryout_sessions', ['id'], unique=False)

    # Create user_achievements table
    op.create_table('user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_type', sa.String(length=50), nullable=False),
        sa.Column('achievement_key', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('current_progress', sa.Integer(), nullable=False),
        sa.Column('target_progress', sa.Integer(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('points_reward', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.String(), nullable=True),
        sa.CheckConstraint("achievement_type IN ('streak', 'completion', 'accuracy', 'speed', 'milestone', 'special')", name='valid_achievement_type'),
        sa.CheckConstraint("category IN ('learning', 'social', 'progress', 'mastery', 'engagement')", name='valid_achievement_category'),
        sa.CheckConstraint("difficulty IN ('bronze', 'silver', 'gold', 'platinum')", name='valid_achievement_difficulty'),
        sa.CheckConstraint('current_progress >= 0 AND current_progress <= target_progress', name='valid_achievement_progress'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'achievement_key', name='unique_user_achievement')
    )
    op.create_index('idx_user_achievements_user', 'user_achievements', ['user_id'], unique=False)
    op.create_index('idx_user_achievements_type', 'user_achievements', ['achievement_type'], unique=False)
    op.create_index('idx_user_achievements_completed', 'user_achievements', ['user_id', 'is_completed'], unique=False)
    op.create_index(op.f('ix_user_achievements_id'), 'user_achievements', ['id'], unique=False)

    # Create tryout_answers table
    op.create_table('tryout_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_answer', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('points_earned', sa.Integer(), nullable=False),
        sa.Column('max_points', sa.Integer(), nullable=False),
        sa.Column('time_taken', sa.Integer(), nullable=False),
        sa.Column('answered_at', sa.String(), nullable=False),
        sa.Column('question_index', sa.Integer(), nullable=False),
        sa.Column('feedback_shown', sa.Boolean(), nullable=False),
        sa.Column('explanation_viewed', sa.Boolean(), nullable=False),
        sa.Column('is_flagged', sa.Boolean(), nullable=False),
        sa.Column('is_skipped', sa.Boolean(), nullable=False),
        sa.CheckConstraint('question_index >= 0', name='valid_question_index'),
        sa.CheckConstraint('time_taken > 0', name='valid_time_taken'),
        sa.CheckConstraint('points_earned >= 0 AND points_earned <= max_points', name='valid_points_earned'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['tryout_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tryout_answers_session', 'tryout_answers', ['session_id'], unique=False)
    op.create_index('idx_tryout_answers_question', 'tryout_answers', ['question_id'], unique=False)
    op.create_index('idx_tryout_answers_session_index', 'tryout_answers', ['session_id', 'question_index'], unique=False)
    op.create_index(op.f('ix_tryout_answers_id'), 'tryout_answers', ['id'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('tryout_answers')
    op.drop_table('user_achievements')
    op.drop_table('tryout_sessions')
    op.drop_table('srs_cards')
    op.drop_table('questionset_questions')
    op.drop_table('question_attempts')
    op.drop_table('payment_transactions')
    op.drop_table('lesson_progress')
    op.drop_table('lesson_questions')
    op.drop_table('subscriptions')
    op.drop_table('question_sets')
    op.drop_table('questions')
    op.drop_table('lessons')
    op.drop_table('user_preferences')
    op.drop_table('users')