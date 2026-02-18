"""
Context-Aware Chat Service
Xử lý 2 loại chat:
- General (Consultant): Hỏi về luật tổng quát, không cần ngữ cảnh luật
- Law Detail: Chat về một luật cụ thể, có ngữ cảnh luật

Features:
- Lưu context (ngữ cảnh luật khi là law-detail)
- Summarize messages mỗi 5 tin nhắn
- Lịch sử session
"""

import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List, Dict, Any
import json

from app import models, schemas
from app.services.law_agent.graph import app as agent_app
from app.services.law_agent.title_generator import generate_chat_title
from app.services.json_search_service import get_json_law_detail

logger = logging.getLogger(__name__)


class ContextAwareChatService:
    """Service xử lý context-aware chat"""

    SUMMARY_THRESHOLD = 5  # Summarize mỗi 5 tin nhắn

    @staticmethod
    async def process_context_chat(
        db: Session,
        current_user: models.User,
        input_data: schemas.QueryInput,
    ) -> schemas.ChatResponse:
        """
        Xử lý chat với ngữ cảnh
        
        Args:
            db: Database session
            current_user: User hiện tại
            input_data: Input data chứa query, session_id, context_type, law_id
        
        Returns:
            ChatResponse
        """
        
        if not input_data.query or not input_data.query.strip():
            raise HTTPException(status_code=400, detail="Empty query.")

        # -------------------------
        # 1. Load or create session
        # -------------------------
        session = None
        context_text = ""

        if input_data.session_id:
            session = db.query(models.ChatSession).filter(
                models.ChatSession.id == input_data.session_id,
                models.ChatSession.user_id == current_user.id
            ).first()

        if not session:
            session = models.ChatSession(
                user_id=current_user.id,
                session_type=input_data.context_type,
                law_id=input_data.law_id if input_data.context_type == "law-detail" else None,
                title=None  # Will be set after first message
            )
            db.add(session)
            db.flush()

        # -------------------------
        # 2. Build chat context
        # -------------------------
        chat_history_text = ContextAwareChatService._build_chat_history(
            db, session.id
        )

        # 3. Add law context if law-detail
        context_text = ""
        if input_data.context_type == "law-detail" and input_data.law_id:
            context_text = ContextAwareChatService._get_law_context(
                db, current_user.id, input_data.law_id
            )

        # -------------------------
        # 4. Build prompt với context
        # -------------------------
        prompt = ContextAwareChatService._build_prompt_with_context(
            query=input_data.query,
            chat_history=chat_history_text,
            law_context=context_text,
            context_type=input_data.context_type,
        )

        # -------------------------
        # 5. Call agent
        # -------------------------
        try:
            inputs = {
                "query": prompt,
                "chat_history": chat_history_text,
            }

            output = await agent_app.ainvoke(inputs)

            final_answer = output.get(
                "generation",
                "Xin lỗi, tôi không thể xử lý yêu cầu này."
            )

            raw_sources = output.get("sources", [])
            formatted_sources = raw_sources if raw_sources else []

        except Exception as e:
            logger.error(f"Agent error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"AI service error: {str(e)}"
            )

        # -------------------------
        # 6. Persist messages
        # -------------------------
        try:
            user_msg = models.Message(
                session_id=session.id,
                sender="user",
                message=input_data.query,
                sources=json.dumps([]),  # User message doesn't have sources
            )

            bot_msg = models.Message(
                session_id=session.id,
                sender="assistant",
                message=final_answer,
                sources=json.dumps(formatted_sources),
            )

            db.add_all([user_msg, bot_msg])
            db.flush()

            # -------------------------
            # 7. Check if need to summarize
            # -------------------------
            messages = db.query(models.Message).filter(
                models.Message.session_id == session.id
            ).all()

            if len(messages) % (ContextAwareChatService.SUMMARY_THRESHOLD * 2) == 0:
                # Summarize last SUMMARY_THRESHOLD messages
                ContextAwareChatService._create_message_summary(
                    db, session.id, messages
                )

            # -------------------------
            # 8. Set title if first message
            # -------------------------
            if not session.title:
                try:
                    session.title = await generate_chat_title(input_data.query)
                except Exception as e:
                    logger.warning(f"Failed to generate title: {e}")
                    session.title = input_data.query[:50]

            db.commit()
            db.refresh(bot_msg)

        except Exception as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Database error."
            )

        return schemas.ChatResponse(
            answer=final_answer,
            sources=formatted_sources,
            session_id=session.id,
            message_id=bot_msg.id,
        )

    @staticmethod
    def _build_chat_history(db: Session, session_id: int) -> str:
        """Build chat history from last messages"""
        messages = db.query(models.Message).filter(
            models.Message.session_id == session_id
        ).order_by(models.Message.created_at.asc()).limit(10).all()

        return "\n".join(
            [f"{msg.sender}: {msg.message}" for msg in messages]
        )

    @staticmethod
    def _get_law_context(db: Session, user_id: int, law_id: str) -> str:
        """Lấy context của luật từ saved laws hoặc từ JSON data"""
        # Thử lấy từ SavedLaw trước
        saved_law = db.query(models.SavedLaw).filter(
            models.SavedLaw.user_id == user_id,
            models.SavedLaw.law_id == law_id
        ).first()

        if saved_law and saved_law.law_content:
            return f"""
Ngữ cảnh luật:
Tiêu đề: {saved_law.law_title}
Loại: {saved_law.law_type}
Năm: {saved_law.law_year}
Cơ quan ban hành: {saved_law.law_authority}

Nội dung:
{saved_law.law_content[:2000]}...
"""
        
        # Nếu không có trong SavedLaw, thử lấy từ JSON data
        try:
            law = get_json_law_detail(law_id)
            if law and law.content:
                return f"""
Ngữ cảnh luật:
Tiêu đề: {law.title}
Loại: {law.type}
Năm: {law.year}
Cơ quan ban hành: {law.authority}

Nội dung:
{law.content[:2000]}...
"""
        except Exception as e:
            logger.warning(f"Failed to fetch law from JSON: {e}")
        
        return ""

    @staticmethod
    def _build_prompt_with_context(
        query: str,
        chat_history: str,
        law_context: str = "",
        context_type: str = "general",
    ) -> str:
        """Build prompt với context"""
        
        if context_type == "law-detail" and law_context:
            return f"""
{law_context}

Lịch sử chat:
{chat_history}

Câu hỏi hiện tại: {query}

Hãy trả lời dựa trên ngữ cảnh luật ở trên.
"""
        else:
            return f"""
Lịch sử chat:
{chat_history}

Câu hỏi: {query}

Hãy trả lời câu hỏi về luật một cách tổng quát.
"""

    @staticmethod
    def _create_message_summary(
        db: Session,
        session_id: int,
        all_messages: List[models.Message],
    ) -> None:
        """Create summary cho messages"""
        
        # Lấy messages từ vị trí cuối cùng
        recent_messages = all_messages[-ContextAwareChatService.SUMMARY_THRESHOLD:]
        
        if not recent_messages:
            return

        messages_text = "\n".join(
            [f"{msg.sender}: {msg.message}" for msg in recent_messages]
        )

        try:
            # TODO: Gọi LLM để summarize
            # Hiện tại sử dụng simple summary
            summary = f"Tóm tắt {len(recent_messages)} tin nhắn gần nhất:\n{messages_text[:500]}..."
            
            summary_obj = models.MessageSummary(
                session_id=session_id,
                summary=summary,
                message_count=len(recent_messages),
            )
            db.add(summary_obj)
            
        except Exception as e:
            logger.warning(f"Failed to create summary: {e}")

    @staticmethod
    def get_session_history(
        db: Session,
        session_id: int,
        user_id: int,
    ) -> schemas.SessionHistory:
        """Lấy lịch sử của một session"""
        
        session = db.query(models.ChatSession).filter(
            models.ChatSession.id == session_id,
            models.ChatSession.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        messages = db.query(models.Message).filter(
            models.Message.session_id == session_id
        ).order_by(models.Message.created_at.asc()).all()

        message_schemas = [
            schemas.MessageWithContext(
                id=msg.id,
                sender=msg.sender,
                message=msg.message,
                sources=json.loads(msg.sources) if msg.sources else [],
                created_at=msg.created_at,
            )
            for msg in messages
        ]

        return schemas.SessionHistory(
            id=session.id,
            session_type=session.session_type,
            law_id=session.law_id,
            title=session.title,
            messages=message_schemas,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    @staticmethod
    def get_summaries_for_session(
        db: Session,
        session_id: int,
        user_id: int,
    ) -> List[schemas.MessageSummaryResponse]:
        """Lấy danh sách summary cho một session"""
        
        # Verify session belongs to user
        session = db.query(models.ChatSession).filter(
            models.ChatSession.id == session_id,
            models.ChatSession.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        summaries = db.query(models.MessageSummary).filter(
            models.MessageSummary.session_id == session_id
        ).order_by(models.MessageSummary.summarized_at.desc()).all()

        return [
            schemas.MessageSummaryResponse(
                id=s.id,
                summary=s.summary,
                message_count=s.message_count,
                summarized_at=s.summarized_at,
            )
            for s in summaries
        ]
