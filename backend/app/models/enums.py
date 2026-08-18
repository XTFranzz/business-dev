import enum


class BusinessStatus(str, enum.Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    REVIEWED = "reviewed"
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
