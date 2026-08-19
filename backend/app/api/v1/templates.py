import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import MessageTemplate
from app.schemas.outreach import MessageTemplateCreate, MessageTemplateRead, MessageTemplateUpdate

router = APIRouter(prefix="/message-templates", tags=["templates"])


@router.get("", response_model=list[MessageTemplateRead])
def list_templates(db: Session = Depends(get_db)) -> list[MessageTemplate]:
    return (
        db.execute(select(MessageTemplate).order_by(MessageTemplate.created_at.desc()))
        .scalars()
        .all()
    )


@router.post("", response_model=MessageTemplateRead, status_code=201)
def create_template(
    payload: MessageTemplateCreate, db: Session = Depends(get_db)
) -> MessageTemplate:
    template = MessageTemplate(**payload.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/{template_id}", response_model=MessageTemplateRead)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> MessageTemplate:
    template = db.get(MessageTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=MessageTemplateRead)
def update_template(
    template_id: uuid.UUID, payload: MessageTemplateUpdate, db: Session = Depends(get_db)
) -> MessageTemplate:
    template = db.get(MessageTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    template = db.get(MessageTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
