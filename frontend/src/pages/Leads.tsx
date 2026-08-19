import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { apiFetch, API_BASE_URL } from "@/lib/api"
import type { BusinessListResponse } from "@/types/api"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const WEBSITE_FILTER_OPTIONS = [
  { value: "any", label: "Any" },
  { value: "false", label: "No website" },
  { value: "true", label: "Has website" },
]

function scoreBadgeVariant(score: number | null): "default" | "secondary" | "outline" {
  if (score === null) return "outline"
  if (score >= 60) return "default"
  return "secondary"
}

export default function Leads() {
  const [search, setSearch] = useState("")
  const [city, setCity] = useState("")
  const [category, setCategory] = useState("")
  const [hasWebsite, setHasWebsite] = useState("any")
  const [minScore, setMinScore] = useState("")
  const [appliedFilters, setAppliedFilters] = useState({
    search: "",
    city: "",
    category: "",
    hasWebsite: "any",
    minScore: "",
  })

  const params = new URLSearchParams({ limit: "100" })
  if (appliedFilters.search) params.set("search", appliedFilters.search)
  if (appliedFilters.city) params.set("city", appliedFilters.city)
  if (appliedFilters.category) params.set("category", appliedFilters.category)
  if (appliedFilters.hasWebsite !== "any") params.set("has_website", appliedFilters.hasWebsite)
  if (appliedFilters.minScore) params.set("min_score", appliedFilters.minScore)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["leads", appliedFilters],
    queryFn: () => apiFetch<BusinessListResponse>(`/leads?${params.toString()}`),
  })

  function applyFilters() {
    setAppliedFilters({ search, city, category, hasWebsite, minScore })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Leads</h1>
          <p className="text-sm text-muted-foreground">
            {data ? `${data.count} businesses discovered` : "Loading..."}
          </p>
        </div>
        <Button variant="outline" asChild>
          <a href={`${API_BASE_URL}/leads/export?${params.toString()}`}>Export CSV</a>
        </Button>
      </div>

      <div className="flex flex-wrap items-end gap-3 rounded-md border p-4">
        <div className="space-y-1.5">
          <Label htmlFor="f-search">Search</Label>
          <Input
            id="f-search"
            placeholder="Business name"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-40"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="f-city">City</Label>
          <Input
            id="f-city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-40"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="f-category">Category</Label>
          <Input
            id="f-category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-40"
          />
        </div>
        <div className="space-y-1.5">
          <Label>Website</Label>
          <Select value={hasWebsite} onValueChange={setHasWebsite}>
            <SelectTrigger className="w-36">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {WEBSITE_FILTER_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="f-score">Min lead score</Label>
          <Input
            id="f-score"
            type="number"
            min={0}
            max={100}
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
            className="w-28"
          />
        </div>
        <Button onClick={applyFilters}>Apply filters</Button>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading leads...</p>}
      {isError && <p className="text-sm text-destructive">{(error as Error).message}</p>}

      {data && data.results.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No leads match these filters — try loosening them, or run a search from Discover.
        </p>
      )}

      {data && data.results.length > 0 && (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Business</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>City</TableHead>
                <TableHead>Website</TableHead>
                <TableHead>Socials</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead>Lead Score</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((b) => (
                <TableRow key={b.id}>
                  <TableCell className="font-medium">
                    <Link to={`/leads/${b.id}`} className="hover:underline">
                      {b.name}
                    </Link>
                  </TableCell>
                  <TableCell>{b.category ?? "—"}</TableCell>
                  <TableCell>{b.location?.city ?? "—"}</TableCell>
                  <TableCell>
                    {b.website?.url ? (
                      <a
                        href={b.website.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary hover:underline"
                      >
                        Found
                      </a>
                    ) : (
                      <Badge variant="secondary">No website</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {b.socials.length > 0 ? b.socials.map((s) => s.platform).join(", ") : "—"}
                  </TableCell>
                  <TableCell>{b.rating ? `${b.rating} (${b.review_count ?? 0})` : "—"}</TableCell>
                  <TableCell>
                    <Badge variant={scoreBadgeVariant(b.lead_score)}>
                      {b.lead_score ?? "—"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{b.status}</Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}
