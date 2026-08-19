import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { toast } from "sonner"
import { apiFetch } from "@/lib/api"
import type { DiscoverJobRead, SavedSearchRead } from "@/types/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function Discover() {
  const queryClient = useQueryClient()
  const [country, setCountry] = useState("Philippines")
  const [state, setState] = useState("")
  const [city, setCity] = useState("")
  const [category, setCategory] = useState("")
  const [maxResults, setMaxResults] = useState(20)
  const [provider, setProvider] = useState("google_places")
  const [jobId, setJobId] = useState<string | null>(null)

  const { data: savedSearches } = useQuery({
    queryKey: ["saved-searches"],
    queryFn: () => apiFetch<SavedSearchRead[]>("/saved-searches"),
  })

  const createJob = useMutation({
    mutationFn: () =>
      apiFetch<DiscoverJobRead>("/discover/jobs", {
        method: "POST",
        body: JSON.stringify({
          country,
          state: state || null,
          city: city || null,
          category,
          max_results: maxResults,
          provider,
        }),
      }),
    onSuccess: (job) => setJobId(job.id),
  })

  const saveSearch = useMutation({
    mutationFn: () =>
      apiFetch<SavedSearchRead>("/saved-searches", {
        method: "POST",
        body: JSON.stringify({
          name: `${category} in ${city || country}`,
          country,
          state: state || null,
          city: city || null,
          category,
          max_results: maxResults,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-searches"] })
      toast.success("Search preset saved")
    },
  })

  const deleteSaved = useMutation({
    mutationFn: (id: string) => apiFetch<void>(`/saved-searches/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["saved-searches"] }),
  })

  function loadSavedSearch(saved: SavedSearchRead) {
    setCountry(saved.params.country)
    setState(saved.params.state ?? "")
    setCity(saved.params.city ?? "")
    setCategory(saved.params.category)
    setMaxResults(saved.params.max_results)
  }

  const jobQuery = useQuery({
    queryKey: ["discover-job", jobId],
    queryFn: () => apiFetch<DiscoverJobRead>(`/discover/jobs/${jobId}`),
    enabled: jobId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === "completed" || status === "failed" ? false : 1500
    },
  })

  const job = jobQuery.data

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Discover</h1>
        <p className="text-sm text-muted-foreground">
          Search for businesses matching your filters, then review them in Leads.
        </p>
      </div>

      {savedSearches && savedSearches.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted-foreground">Saved searches:</span>
          {savedSearches.map((saved) => (
            <div key={saved.id} className="flex items-center gap-1">
              <Button variant="outline" size="sm" onClick={() => loadSavedSearch(saved)}>
                {saved.name}
              </Button>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => deleteSaved.mutate(saved.id)}
                aria-label="Delete saved search"
              >
                ×
              </Button>
            </div>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">New search</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label>Data source</Label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="google_places">Google Places (ratings, reviews)</SelectItem>
                <SelectItem value="overpass">OpenStreetMap (free, no ratings)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="country">Country</Label>
              <Input id="country" value={country} onChange={(e) => setCountry(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="state">State / region (optional)</Label>
              <Input id="state" value={state} onChange={(e) => setState(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="city">City</Label>
              <Input id="city" value={city} onChange={(e) => setCity(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                placeholder="e.g. coffee shops"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="max_results">Max results</Label>
              <Input
                id="max_results"
                type="number"
                min={1}
                max={60}
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={() => createJob.mutate()}
              disabled={!category || !country || createJob.isPending || job?.status === "running"}
            >
              {createJob.isPending ? "Starting..." : "Find Leads"}
            </Button>
            <Button
              variant="outline"
              onClick={() => saveSearch.mutate()}
              disabled={!category || !country || saveSearch.isPending}
            >
              Save search
            </Button>
          </div>

          {createJob.isError && (
            <p className="text-sm text-destructive">{(createJob.error as Error).message}</p>
          )}
        </CardContent>
      </Card>

      {job && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {job.status === "completed"
                ? "Search complete"
                : job.status === "failed"
                  ? "Search failed"
                  : "Searching..."}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>Found: {job.found_count}</p>
            <p>Processed: {job.processed_count}</p>
            {job.error && <p className="text-destructive">{job.error}</p>}
            {job.status === "completed" && (
              <Button asChild variant="outline" size="sm">
                <Link to="/leads">View leads</Link>
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
