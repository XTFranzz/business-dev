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

export type BusinessStatus = "new" | "qualified" | "reviewed" | "archived" | "do_not_contact"

export type SearchJobStatus = "pending" | "running" | "completed" | "failed"

export interface LocationRead {
  country: string | null
  state: string | null
  city: string | null
  address: string | null
}

export interface WebsiteRead {
  url: string | null
  status: WebsiteStatus
}

export interface SocialRead {
  platform: SocialPlatform
  url: string
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
}

export interface BusinessListResponse {
  count: number
  results: BusinessListItem[]
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
