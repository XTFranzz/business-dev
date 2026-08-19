import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.session import get_db
from app.models import Business, Campaign, CampaignLead, Message, MessageTemplate
from app.models.enums import (
    BusinessStatus,
    CampaignLeadStatus,
    CampaignStatus,
    ContactType,
    MessageChannel,
    MessageStatus,
)
from app.schemas.outreach import (
    CampaignCreate,
    CampaignDetail,
    CampaignLeadRead,
    CampaignProcessResult,
    CampaignRead,
    CampaignUpdate,
    MessageRead,
)
from app.services.leads.query import build_filtered_leads_query
from app.services.messaging.email_sender import send_email
from app.services.messaging.suppression import is_suppressed
from app.services.messaging.templating import render_template

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _counts(campaign: Campaign) -> dict:
    counts = {
        "lead_count": len(campaign.campaign_leads),
        "pending_approval_count": 0,
        "approved_count": 0,
        "sent_count": 0,
        "failed_count": 0,
    }
    for campaign_lead in campaign.campaign_leads:
        if campaign_lead.status == CampaignLeadStatus.PENDING:
            counts["pending_approval_count"] += 1
        elif campaign_lead.status == CampaignLeadStatus.APPROVED:
            counts["approved_count"] += 1
        elif campaign_lead.status == CampaignLeadStatus.SENT:
            counts["sent_count"] += 1
        elif campaign_lead.status == CampaignLeadStatus.FAILED:
            counts["failed_count"] += 1
    return counts


def _to_campaign_read(campaign: Campaign) -> CampaignRead:
    return CampaignRead(
        id=campaign.id,
        name=campaign.name,
        template_id=campaign.template_id,
        filter_params=campaign.filter_params,
        daily_send_limit=campaign.daily_send_limit,
        follow_up_days=campaign.follow_up_days,
        status=campaign.status,
        created_at=campaign.created_at,
        **_counts(campaign),
    )


def _profile_url(business: Business) -> str | None:
    if business.socials:
        return business.socials[0].url
    return business.source_url


def _to_campaign_detail(campaign: Campaign) -> CampaignDetail:
    leads = [
        CampaignLeadRead(
            id=cl.id,
            business_id=cl.business_id,
            business_name=cl.business.name,
            profile_url=_profile_url(cl.business),
            status=cl.status,
            message=MessageRead.model_validate(cl.message) if cl.message else None,
        )
        for cl in campaign.campaign_leads
    ]
    return CampaignDetail(**_to_campaign_read(campaign).model_dump(), leads=leads)


def _load_campaign(db: Session, campaign_id: uuid.UUID) -> Campaign | None:
    return (
        db.execute(
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(
                selectinload(Campaign.campaign_leads)
                .selectinload(CampaignLead.business)
                .selectinload(Business.socials),
                selectinload(Campaign.campaign_leads)
                .selectinload(CampaignLead.business)
                .selectinload(Business.contacts),
                selectinload(Campaign.campaign_leads).selectinload(CampaignLead.message),
            )
        )
        .scalars()
        .first()
    )


@router.get("", response_model=list[CampaignRead])
def list_campaigns(db: Session = Depends(get_db)) -> list[CampaignRead]:
    campaigns = (
        db.execute(
            select(Campaign)
            .options(selectinload(Campaign.campaign_leads))
            .order_by(Campaign.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_to_campaign_read(c) for c in campaigns]


@router.post("", response_model=CampaignDetail, status_code=201)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)) -> CampaignDetail:
    template = db.get(MessageTemplate, payload.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    filter_kwargs = payload.filter_kwargs()

    campaign = Campaign(
        name=payload.name,
        template_id=payload.template_id,
        filter_params=filter_kwargs,
        daily_send_limit=payload.daily_send_limit,
        follow_up_days=payload.follow_up_days,
    )
    db.add(campaign)
    db.flush()

    query = build_filtered_leads_query(**filter_kwargs).where(
        Business.status != BusinessStatus.DO_NOT_CONTACT
    )
    businesses = (
        db.execute(
            query.options(selectinload(Business.contacts), selectinload(Business.socials))
        )
        .unique()
        .scalars()
        .all()
    )

    for business in businesses:
        campaign_lead = CampaignLead(campaign_id=campaign.id, business_id=business.id)
        db.add(campaign_lead)
        db.flush()

        email = next((c.value for c in business.contacts if c.type == ContactType.EMAIL), None)
        channel = MessageChannel.EMAIL if email else MessageChannel.MANUAL_COPY

        db.add(
            Message(
                business_id=business.id,
                campaign_lead_id=campaign_lead.id,
                channel=channel,
                subject=render_template(template.subject, business),
                body=render_template(template.body, business),
                status=MessageStatus.PENDING_APPROVAL,
            )
        )

    db.commit()
    campaign = _load_campaign(db, campaign.id)
    return _to_campaign_detail(campaign)


@router.get("/{campaign_id}", response_model=CampaignDetail)
def get_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)) -> CampaignDetail:
    campaign = _load_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _to_campaign_detail(campaign)


@router.delete("/{campaign_id}", status_code=204)
def delete_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign)
    db.commit()


@router.patch("/{campaign_id}", response_model=CampaignDetail)
def update_campaign(
    campaign_id: uuid.UUID, payload: CampaignUpdate, db: Session = Depends(get_db)
) -> CampaignDetail:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if payload.status is not None:
        campaign.status = payload.status
    if payload.daily_send_limit is not None:
        campaign.daily_send_limit = payload.daily_send_limit
    db.commit()
    campaign = _load_campaign(db, campaign_id)
    return _to_campaign_detail(campaign)


@router.post("/{campaign_id}/process", response_model=CampaignProcessResult)
def process_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)) -> CampaignProcessResult:
    campaign = _load_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(
            status_code=400, detail="Campaign must be active to send (set status to 'active')"
        )

    has_approved_email_message = any(
        cl.status == CampaignLeadStatus.APPROVED
        and cl.message is not None
        and cl.message.channel == MessageChannel.EMAIL
        for cl in campaign.campaign_leads
    )
    settings = get_settings()
    if has_approved_email_message and not (
        settings.gmail_address and settings.gmail_app_password
    ):
        raise HTTPException(
            status_code=503,
            detail="GMAIL_ADDRESS / GMAIL_APP_PASSWORD are not set in backend/.env",
        )

    sent = failed = skipped = 0
    remaining = campaign.daily_send_limit

    for campaign_lead in campaign.campaign_leads:
        if remaining <= 0:
            break
        if campaign_lead.status != CampaignLeadStatus.APPROVED:
            continue
        message = campaign_lead.message
        if message is None or message.channel != MessageChannel.EMAIL:
            continue

        business = campaign_lead.business
        email = next(
            (c.value for c in business.contacts if c.type == ContactType.EMAIL), None
        )
        reason = is_suppressed(db, business, email)
        if reason or not email:
            campaign_lead.status = CampaignLeadStatus.SKIPPED
            skipped += 1
            continue

        try:
            send_email(email, message.subject, message.body)
        except Exception:  # noqa: BLE001 - persisted as this message's own failure state
            message.status = MessageStatus.FAILED
            campaign_lead.status = CampaignLeadStatus.FAILED
            failed += 1
            continue

        message.status = MessageStatus.SENT
        message.sent_at = message.sent_at or datetime.now(timezone.utc)
        campaign_lead.status = CampaignLeadStatus.SENT
        if business.status in (
            BusinessStatus.NEW,
            BusinessStatus.QUALIFIED,
            BusinessStatus.REVIEWED,
        ):
            business.status = BusinessStatus.CONTACTED
        sent += 1
        remaining -= 1

    db.commit()
    return CampaignProcessResult(sent=sent, failed=failed, skipped=skipped)
