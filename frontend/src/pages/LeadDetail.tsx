import { useParams } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiFetch } from "@/lib/api"
import type { BusinessDetail, BusinessStatus } from "@/types/api"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const STATUS_OPTIONS: BusinessStatus[] = [
  "new",
  "qualified",
  "reviewed",
  "archived",
  "do_not_contact",
]

function scoreBadgeVariant(score: number | null | undefined): "default" | "secondary" | "outline" {
  if (score === null || score === undefined) return "outline"
  if (score >= 60) return "default"
  return "secondary"
}

export default function LeadDetail() {
  const { id } = useParams()
  const queryClient = useQueryClient()

  const { data: business, isLoading, isError, error } = useQuery({
    queryKey: ["lead", id],
    queryFn: () => apiFetch<BusinessDetail>(`/leads/${id}`),
    enabled: !!id,
  })

  const updateStatus = useMutation({
    mutationFn: (status: BusinessStatus) =>
      apiFetch<BusinessDetail>(`/leads/${id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(["lead", id], updated)
      queryClient.invalidateQueries({ queryKey: ["leads"] })
    },
  })

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>
  if (isError) return <p className="text-sm text-destructive">{(error as Error).message}</p>
  if (!business) return null

  const website = business.website
  const analysis = website?.analysis

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{business.name}</h1>
          <p className="text-sm text-muted-foreground">
            {[business.location?.city, business.location?.country].filter(Boolean).join(", ")}
            {business.category ? ` · ${business.category}` : ""}
          </p>
        </div>
        <Select
          value={business.status}
          onValueChange={(value) => updateStatus.mutate(value as BusinessStatus)}
        >
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((s) => (
              <SelectItem key={s} value={s}>
                {s.replace(/_/g, " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Website</CardTitle>
          </CardHeader>
          <CardContent>
            {website?.url ? (
              <a
                href={website.url}
                target="_blank"
                rel="noreferrer"
                className="text-sm text-primary hover:underline"
              >
                {website.status}
              </a>
            ) : (
              <Badge variant="secondary">No website</Badge>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Website Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{analysis?.quality_score ?? "—"}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Lead Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant={scoreBadgeVariant(business.lead_score?.score)} className="text-base">
              {business.lead_score?.score ?? "—"}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">
              {business.rating ? `${business.rating}` : "—"}
            </span>
            {business.review_count !== null && (
              <span className="ml-1 text-sm text-muted-foreground">
                ({business.review_count})
              </span>
            )}
          </CardContent>
        </Card>
      </div>

      {business.lead_score && business.lead_score.reasons.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Why this is a good lead</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1 text-sm">
              {business.lead_score.reasons.map((reason) => (
                <li key={reason}>✓ {reason}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Contact</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          {business.contacts.length === 0 && (
            <p className="text-muted-foreground">No contact info found.</p>
          )}
          {business.contacts.map((c) => (
            <p key={`${c.type}-${c.value}`}>
              <span className="text-muted-foreground">{c.type}:</span> {c.value}
            </p>
          ))}
          {business.socials.map((s) => (
            <p key={s.url}>
              <span className="text-muted-foreground">{s.platform}:</span>{" "}
              <a href={s.url} target="_blank" rel="noreferrer" className="hover:underline">
                {s.url}
              </a>
            </p>
          ))}
          {business.location?.address && (
            <p>
              <span className="text-muted-foreground">address:</span> {business.location.address}
            </p>
          )}
        </CardContent>
      </Card>

      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Website analysis</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-2 text-sm">
            <p>
              <span className="text-muted-foreground">HTTPS:</span> {analysis.https ? "yes" : "no"}
            </p>
            <p>
              <span className="text-muted-foreground">Mobile-friendly:</span>{" "}
              {analysis.mobile_viewport_present ? "yes" : "no"}
            </p>
            <p>
              <span className="text-muted-foreground">Load time:</span> {analysis.load_time_ms} ms
            </p>
            <p>
              <span className="text-muted-foreground">Pages checked:</span>{" "}
              {analysis.pages_crawled ?? "—"}
            </p>
            <p>
              <span className="text-muted-foreground">Contact form:</span>{" "}
              {analysis.has_contact_form ? "yes" : "no"}
            </p>
            <p>
              <span className="text-muted-foreground">Booking form:</span>{" "}
              {analysis.has_booking_form ? "yes" : "no"}
            </p>
            <p>
              <span className="text-muted-foreground">Broken links:</span>{" "}
              {analysis.broken_links_count ?? "—"}
            </p>
            <p>
              <span className="text-muted-foreground">SEO score:</span> {analysis.seo_score ?? "—"}
            </p>
            {analysis.page_title && (
              <p className="col-span-2">
                <span className="text-muted-foreground">Title:</span> {analysis.page_title}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {business.source_url && (
        <a
          href={business.source_url}
          target="_blank"
          rel="noreferrer"
          className="text-sm text-primary hover:underline"
        >
          View on Google Maps
        </a>
      )}
    </div>
  )
}
