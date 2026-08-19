from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_leads: int
    new_leads: int
    no_website: int
    high_opportunity: int
    contacted: int
    replied: int
    interested: int
    converted: int
