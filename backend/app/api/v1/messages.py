import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Message, MessageEvent
from app.models.enums import BusinessStatus, CampaignLeadStatus, MessageEventType, MessageStatus
from app.schemas.outreach import MessageRead, MessageUpdate

router = APIRouter(prefix="/messages", tags=["messages"])


def _get_message(db: Session, message_id: uuid.UUID) -> Message:
    message = db.get(Message, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.patch("/{message_id}", response_model=MessageRead)
def update_message(
    message_id: uuid.UUID, payload: MessageUpdate, db: Session = Depends(get_db)
) -> Message:
    message = _get_message(db, message_id)
    if message.status not in (MessageStatus.DRAFT, MessageStatus.PENDING_APPROVAL):
        raise HTTPException(status_code=400, detail="Only unsent messages can be edited")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(message, field, value)
    db.commit()
    db.refresh(message)
    return message


@router.post("/{message_id}/approve", response_model=MessageRead)
def approve_message(message_id: uuid.UUID, db: Session = Depends(get_db)) -> Message:
    message = _get_message(db, message_id)
    message.status = MessageStatus.APPROVED
    if message.campaign_lead is not None:
        message.campaign_lead.status = CampaignLeadStatus.APPROVED
        message.campaign_lead.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(message)
    return message


@router.post("/{message_id}/skip", response_model=MessageRead)
def skip_message(message_id: uuid.UUID, db: Session = Depends(get_db)) -> Message:
    message = _get_message(db, message_id)
    if message.campaign_lead is not None:
        message.campaign_lead.status = CampaignLeadStatus.SKIPPED
    db.commit()
    db.refresh(message)
    return message


@router.post("/{message_id}/mark-replied", response_model=MessageRead)
def mark_replied(message_id: uuid.UUID, db: Session = Depends(get_db)) -> Message:
    message = _get_message(db, message_id)
    db.add(MessageEvent(message_id=message.id, event_type=MessageEventType.REPLIED))
    message.business.status = BusinessStatus.REPLIED
    db.commit()
    db.refresh(message)
    return message
