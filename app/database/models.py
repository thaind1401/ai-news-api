import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.db import Base

class Source(Base):
    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint("risk_level IN ('A','B','C')", name="ck_sources_risk_level"),
        CheckConstraint("status IN ('active','paused','blocked')", name="ck_sources_status"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    source_type = Column(Text, nullable=False)
    base_url = Column(Text, nullable=False)
    ingest_method = Column(Text, nullable=False)
    risk_level = Column(Text, nullable=False)
    terms_reviewed = Column(Boolean, nullable=False, default=False)
    robots_reviewed = Column(Boolean, nullable=False, default=False)
    auth_required = Column(Boolean, nullable=False, default=False)
    paywall = Column(Boolean, nullable=False, default=False)
    store_full_text = Column(Boolean, nullable=False, default=False)
    status = Column(Text, nullable=False, default="active")
    owner = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    fetch_runs = relationship("SourceFetchRun", back_populates="source")
    raw_items = relationship("RawItem", back_populates="source")
    signals = relationship("Signal", back_populates="source")


class SourceFetchRun(Base):
    __tablename__ = "source_fetch_runs"
    __table_args__ = (
        CheckConstraint("status IN ('running','success','failed')", name="ck_source_fetch_runs_status"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(BigInteger, ForeignKey("sources.id"), nullable=False, index=True)
    status = Column(Text, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    finished_at = Column(DateTime(timezone=True))
    items_fetched = Column(Integer, nullable=False, default=0)
    items_created = Column(Integer, nullable=False, default=0)
    error_message = Column(Text)
    run_metadata = Column(JSON, nullable=False, default=dict)

    source = relationship("Source", back_populates="fetch_runs")
    raw_items = relationship("RawItem", back_populates="fetch_run")


class RawItem(Base):
    __tablename__ = "raw_items"
    __table_args__ = (
        UniqueConstraint("source_id", "source_url", name="uq_raw_items_source_url"),
        UniqueConstraint("source_id", "external_id", name="uq_raw_items_external_id"),
        CheckConstraint("parse_status IN ('pending','parsed','failed')", name="ck_raw_items_parse_status"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(BigInteger, ForeignKey("sources.id"), nullable=False, index=True)
    fetch_run_id = Column(BigInteger, ForeignKey("source_fetch_runs.id"), index=True)
    external_id = Column(Text)
    source_url = Column(Text, nullable=False)
    title = Column(Text)
    published_at = Column(DateTime(timezone=True), index=True)
    raw_payload = Column(JSON, nullable=False, default=dict)
    parse_status = Column(Text, nullable=False, default="pending", index=True)
    parse_error = Column(Text)
    fetched_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    source = relationship("Source", back_populates="raw_items")
    fetch_run = relationship("SourceFetchRun", back_populates="raw_items")
    signal = relationship("Signal", back_populates="raw_item", uselist=False)


class Company(Base):
    __tablename__ = "companies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    normalized_name = Column(Text, nullable=False, unique=True)
    website = Column(Text)
    domain = Column(Text, index=True)
    company_type = Column(Text)
    country_code = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    signals = relationship("Signal", back_populates="company")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    slug = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    signals = relationship("Signal", back_populates="primary_topic")


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_signals_dedup_key"),
        CheckConstraint(
            "event_type IN ('funding','product_launch','hiring','partnership','acquisition','market_move','regulation','competitor_update')",
            name="ck_signals_event_type",
        ),
        CheckConstraint("signal_status IN ('active','hidden','rejected')", name="ck_signals_status"),
        CheckConstraint("visibility IN ('public','internal')", name="ck_signals_visibility"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(BigInteger, ForeignKey("sources.id"), nullable=False, index=True)
    raw_item_id = Column(BigInteger, ForeignKey("raw_items.id"), nullable=False, unique=True)
    source_url = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    raw_excerpt = Column(Text)
    author_name = Column(Text)
    image_url = Column(Text)
    published_at = Column(DateTime(timezone=True), index=True)
    crawl_time = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    company_id = Column(BigInteger, ForeignKey("companies.id"), index=True)
    primary_topic_id = Column(BigInteger, ForeignKey("topics.id"), index=True)
    event_type = Column(Text, nullable=False, default="market_move", index=True)
    dedup_key = Column(Text, nullable=False)
    signal_status = Column(Text, nullable=False, default="active")
    visibility = Column(Text, nullable=False, default="public")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    source = relationship("Source", back_populates="signals")
    raw_item = relationship("RawItem", back_populates="signal")
    company = relationship("Company", back_populates="signals")
    primary_topic = relationship("Topic", back_populates="signals")
    ai_enrichment = relationship("SignalAIEnrichment", back_populates="signal", uselist=False)
    embedding = relationship("SignalEmbedding", back_populates="signal", uselist=False)


class SignalAIEnrichment(Base):
    __tablename__ = "signal_ai_enrichments"
    __table_args__ = (
        CheckConstraint("importance_score IS NULL OR (importance_score >= 1 AND importance_score <= 5)", name="ck_signal_ai_importance_score"),
        CheckConstraint("enrichment_status IN ('pending','done','failed')", name="ck_signal_ai_status"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    signal_id = Column(BigInteger, ForeignKey("signals.id"), nullable=False, unique=True, index=True)
    summary_one_line = Column(Text)
    summary_bullets = Column(JSON, nullable=False, default=list)
    why_it_matters = Column(Text)
    tags = Column(JSON, nullable=False, default=list)
    importance_score = Column(Integer)
    confidence_score = Column(Numeric(5, 4))
    company_name_extracted = Column(Text)
    topic_extracted = Column(Text)
    event_type_extracted = Column(Text)
    model_name = Column(Text, nullable=False)
    prompt_version = Column(Text, nullable=False)
    enrichment_status = Column(Text, nullable=False, default="done")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    signal = relationship("Signal", back_populates="ai_enrichment")


class SignalEmbedding(Base):
    __tablename__ = "signal_embeddings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    signal_id = Column(BigInteger, ForeignKey("signals.id"), nullable=False, unique=True, index=True)
    embedding_text = Column(Text, nullable=False)
    embedding_model = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    signal = relationship("Signal", back_populates="embedding")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user','admin')", name="ck_users_role"),
        CheckConstraint("status IN ('active','disabled')", name="ck_users_status"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text)
    role = Column(Text, nullable=False, default="user")
    status = Column(Text, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    bookmarks = relationship("Bookmark", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    watchlists = relationship("Watchlist", back_populates="user")
    digests = relationship("Digest", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "signal_id", name="uq_bookmarks_user_signal"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    signal_id = Column(BigInteger, ForeignKey("signals.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="bookmarks")
    signal = relationship("Signal")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    preferred_topics = Column(JSON, nullable=False, default=list)
    preferred_event_types = Column(JSON, nullable=False, default=list)
    preferred_companies = Column(JSON, nullable=False, default=list)
    digest_enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="preferences")


class Watchlist(Base):
    __tablename__ = "watchlists"
    __table_args__ = (
        UniqueConstraint("user_id", "watch_type", "watch_value", name="uq_watchlists_user_type_value"),
        CheckConstraint("watch_type IN ('company','topic','event_type')", name="ck_watchlists_type"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    watch_type = Column(Text, nullable=False)
    watch_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="watchlists")


class Digest(Base):
    __tablename__ = "digests"
    __table_args__ = (
        CheckConstraint("digest_type IN ('daily','weekly')", name="ck_digests_type"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    digest_date = Column(Date, nullable=False, index=True)
    digest_type = Column(Text, nullable=False, default="daily")
    title = Column(Text, nullable=False)
    content = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="digests")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    title = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user','assistant','system')", name="ck_chat_messages_role"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=False, default=list)
    model_name = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)

    session = relationship("ChatSession", back_populates="messages")
