export type WebsiteStatus =
  | "none"
  | "found"
  | "unreachable"
  | "redirects_to_social"
  | "incomplete"
  | "outdated"
  | "directory"
  | "needs_review"

export type SocialPlatform = "facebook" | "instagram" | "tiktok" | "linkedin" | "other"

export type BusinessStatus =
  | "new"
  | "qualified"
  | "reviewed"
  | "contacted"
  | "replied"
  | "interested"
  | "not_interested"
  | "won"
  | "archived"
  | "do_not_contact"

export type SearchJobStatus = "pending" | "running" | "completed" | "failed"

export interface LocationRead {
  country: string | null
  state: string | null
  city: string | null
  address: string | null
}

export interface WebsiteAnalysisRead {
  http_status: number | null
  https: boolean | null
  ssl_valid: boolean | null
  final_redirect_url: string | null
  page_title: string | null
  meta_description: string | null
  mobile_viewport_present: boolean | null
  load_time_ms: number | null
  pages_crawled: number | null
  has_contact_form: boolean | null
  has_booking_form: boolean | null
  broken_links_count: number | null
  seo_score: number | null
  quality_score: number | null
  analyzed_at: string
}

export interface WebsiteRead {
  url: string | null
  status: WebsiteStatus
  analysis: WebsiteAnalysisRead | null
}

export interface SocialRead {
  platform: SocialPlatform
  url: string
}

export type ContactType = "phone" | "email"

export interface ContactRead {
  type: ContactType
  value: string
  is_primary: boolean
}

export interface LeadScoreRead {
  score: number
  reasons: string[]
  computed_at: string
}

export interface BusinessListItem {
  id: string
  name: string
  category: string | null
  status: BusinessStatus
  rating: number | null
  review_count: number | null
  discovered_at: string
  location: LocationRead | null
  website: WebsiteRead | null
  socials: SocialRead[]
  has_phone: boolean
  has_email: boolean
  lead_score: number | null
}

export interface BusinessListResponse {
  count: number
  results: BusinessListItem[]
}

export interface BusinessDetail {
  id: string
  name: string
  category: string | null
  description: string | null
  status: BusinessStatus
  source: string | null
  source_url: string | null
  rating: number | null
  review_count: number | null
  discovered_at: string
  location: LocationRead | null
  website: WebsiteRead | null
  socials: SocialRead[]
  contacts: ContactRead[]
  lead_score: LeadScoreRead | null
}

export interface DashboardStats {
  total_leads: number
  new_leads: number
  no_website: number
  high_opportunity: number
  contacted: number
  replied: number
  interested: number
  converted: number
}

export interface DiscoverJobRead {
  id: string
  status: SearchJobStatus
  found_count: number
  processed_count: number
  checked_count: number
  qualified_count: number
  error: string | null
  started_at: string | null
  completed_at: string | null
}

export interface SavedSearchRead {
  id: string
  name: string
  params: {
    country: string
    state: string | null
    city: string | null
    category: string
    max_results: number
  }
  created_at: string
}

// --- Outreach (Phase 3) ---

export interface MessageTemplateRead {
  id: string
  name: string
  subject: string
  body: string
  created_at: string
}

export type CampaignStatus = "draft" | "active" | "paused" | "completed"
export type CampaignLeadStatus = "pending" | "approved" | "sent" | "failed" | "skipped"
export type MessageChannel = "email" | "manual_copy"
export type MessageStatus = "draft" | "pending_approval" | "approved" | "sent" | "failed"

export interface MessageRead {
  id: string
  business_id: string
  channel: MessageChannel
  subject: string
  body: string
  status: MessageStatus
  sent_at: string | null
}

export interface CampaignLeadRead {
  id: string
  business_id: string
  business_name: string
  profile_url: string | null
  status: CampaignLeadStatus
  message: MessageRead | null
}

export interface CampaignRead {
  id: string
  name: string
  template_id: string
  filter_params: Record<string, unknown>
  daily_send_limit: number
  follow_up_days: number | null
  status: CampaignStatus
  created_at: string
  lead_count: number
  pending_approval_count: number
  approved_count: number
  sent_count: number
  failed_count: number
}

export interface CampaignDetail extends CampaignRead {
  leads: CampaignLeadRead[]
}

export interface CampaignProcessResult {
  sent: number
  failed: number
  skipped: number
}

// --- Analytics (Phase 4) ---

export interface CountBucket {
  label: string
  count: number
}

export interface AnalyticsResponse {
  by_country: CountBucket[]
  by_city: CountBucket[]
  by_category: CountBucket[]
  by_website_status: CountBucket[]
  by_status: CountBucket[]
  leads_over_time: CountBucket[]
  messages_sent: number
  messages_failed: number
  replies: number
}
