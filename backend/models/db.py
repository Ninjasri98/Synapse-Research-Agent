"""
SQLAlchemy models for the database.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

from sqlalchemy import String, Text, ForeignKey, JSON, DateTime, func, Enum as SQLEnum, Index
from sqlalchemy.orm import declarative_base, relationship, mapped_column, Mapped

# Base class for SQLAlchemy models
Base = declarative_base()

class NotebookProcessingStatusValue(str, Enum):
    """Enum for notebook processing status values."""
    IN_QUEUE = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"

class NotebookDocumentSourceType(str, Enum):
    """Enum for notebook document source types."""
    UPLOAD = "UPLOAD"
    URL = "URL"
    MANUAL = "MANUAL"

class Task(Base):
    """Task model for the database."""
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    notebook_id: Mapped[str] = mapped_column(String(36), nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sources: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "task_id": self.id,
            "notebook_id": self.notebook_id,
            "topic": self.topic,
            "sources": self.sources,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "failed_at": self.failed_at,
            "result": self.result,
            "error": self.error
        }

class Notebook(Base):
    """Notebook model for the database."""
    __tablename__ = "notebooks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, name="userId", nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    topic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, name="createdAt", nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, name="updatedAt", nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    sources: Mapped[List["NotebookSource"]] = relationship("NotebookSource", back_populates="notebook", cascade="all, delete-orphan")
    output: Mapped[Optional["NotebookOutput"]] = relationship("NotebookOutput", back_populates="notebook", uselist=False, cascade="all, delete-orphan")
    processing_status: Mapped[Optional["NotebookProcessingStatus"]] = relationship("NotebookProcessingStatus", back_populates="notebook", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_notebooks_user_id', user_id),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "topic": self.topic,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class NotebookSource(Base):
    """NotebookSource model for the database."""
    __tablename__ = "notebook_sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    notebook_id: Mapped[str] = mapped_column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), name="notebookId", nullable=False)
    source_type: Mapped[NotebookDocumentSourceType] = mapped_column(
        SQLEnum(
            NotebookDocumentSourceType,
            name="NotebookDocumentSourceType",
            create_type=False
        ),
        name="sourceType",
        nullable=False
    )
    source_url: Mapped[Optional[str]] = mapped_column(String, name="sourceUrl", nullable=True)
    source_url_text: Mapped[Optional[str]] = mapped_column(String, name="sourceUrlText", nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String, name="filePath", nullable=True)
    filename: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, name="createdAt", nullable=False, default=func.now())

    # Relationship
    notebook: Mapped["Notebook"] = relationship("Notebook", back_populates="sources")

    __table_args__ = (
        Index('ix_notebook_sources_notebook_id', notebook_id),
    )

class NotebookOutput(Base):
    """NotebookOutput model for the database."""
    __tablename__ = "notebook_outputs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    notebook_id: Mapped[str] = mapped_column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), name="notebookId", nullable=False, unique=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    audio_overview_url: Mapped[Optional[str]] = mapped_column(String, name="audioOverviewUrl", nullable=True)
    mindmap: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, name="createdAt", nullable=False, default=func.now())

    # Relationships
    notebook: Mapped["Notebook"] = relationship("Notebook", back_populates="output")
    faqs: Mapped[List["NotebookFAQ"]] = relationship("NotebookFAQ", back_populates="notebook_output", cascade="all, delete-orphan")

class NotebookFAQ(Base):
    """NotebookFAQ model for the database."""
    __tablename__ = "notebook_faqs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, name="createdAt", nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, name="updatedAt", nullable=False, default=func.now(), onupdate=func.now())
    notebook_output_id: Mapped[str] = mapped_column(String, ForeignKey("notebook_outputs.id", ondelete="CASCADE"), name="notebookOutputId", nullable=False)

    # Relationship
    notebook_output: Mapped["NotebookOutput"] = relationship("NotebookOutput", back_populates="faqs")

    __table_args__ = (
        Index('ix_notebook_faqs_notebook_output_id', notebook_output_id),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notebook_output_id": self.notebook_output_id
        }

class NotebookProcessingStatus(Base):
    """NotebookProcessingStatus model for the database."""
    __tablename__ = "notebook_processing_status"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[NotebookProcessingStatusValue] = mapped_column(
        SQLEnum(
            NotebookProcessingStatusValue,
            name="NotebookProcessingStatusValue",
            create_type=False
        ),
        nullable=False,
        default=NotebookProcessingStatusValue.IN_QUEUE
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, name="createdAt", nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, name="updatedAt", nullable=False, default=func.now(), onupdate=func.now())
    notebook_id: Mapped[str] = mapped_column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), name="notebookId", nullable=False, unique=True)

    # Relationship
    notebook: Mapped["Notebook"] = relationship("Notebook", back_populates="processing_status")