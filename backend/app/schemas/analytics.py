from pydantic import BaseModel


class CountBucket(BaseModel):
    label: str
    count: int


class AnalyticsResponse(BaseModel):
    by_country: list[CountBucket]
    by_city: list[CountBucket]
    by_category: list[CountBucket]
    by_website_status: list[CountBucket]
    by_status: list[CountBucket]
    leads_over_time: list[CountBucket]
    messages_sent: int
    messages_failed: int
    replies: int
