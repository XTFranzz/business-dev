import enum


class BusinessStatus(str, enum.Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    REVIEWED = "reviewed"
    CONTACTED = "contacted"
    REPLIED = "replied"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    WON = "won"
    ARCHIVED = "archived"
    DO_NOT_CONTACT = "do_not_contact"


class WebsiteStatus(str, enum.Enum):
    NONE = "none"
    FOUND = "found"
    UNREACHABLE = "unreachable"
    REDIRECTS_TO_SOCIAL = "redirects_to_social"
    INCOMPLETE = "incomplete"
    OUTDATED = "outdated"
    DIRECTORY = "directory"
    NEEDS_REVIEW = "needs_review"


class SocialPlatform(str, enum.Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    OTHER = "other"


class ContactType(str, enum.Enum):
    PHONE = "phone"
    EMAIL = "email"


class SearchJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ApiProviderType(str, enum.Enum):
    DISCOVERY = "discovery"
    WEBSITE = "website"
    AI = "ai"


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class CampaignLeadStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class MessageChannel(str, enum.Enum):
    EMAIL = "email"
    MANUAL_COPY = "manual_copy"


class MessageStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    FAILED = "failed"


class MessageEventType(str, enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    REPLIED = "replied"
    UNSUBSCRIBED = "unsubscribed"
