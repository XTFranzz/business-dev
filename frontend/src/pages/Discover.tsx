import { useState } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { apiFetch } from "@/lib/api"
import type { DiscoverJobRead } from "@/types/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Discover() {
  const [country, setCountry] = useState("Philippines")
  const [state, setState] = useState("")
  const [city, setCity] = useState("")
  const [category, setCategory] = useState("")
  const [maxResults, setMaxResults] = useState(20)
  const [jobId, setJobId] = useState<string | null>(null)

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
        }),
      }),
    onSuccess: (job) => setJobId(job.id),
  })

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
          Search Google Places for businesses matching your filters, then review them in Leads.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">New search</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
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

          <Button
            onClick={() => createJob.mutate()}
            disabled={
              !category || !country || createJob.isPending || job?.status === "running"
            }
          >
            {createJob.isPending ? "Starting..." : "Find Leads"}
          </Button>

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
