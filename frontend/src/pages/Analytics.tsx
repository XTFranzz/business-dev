import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "@/lib/api"
import type { AnalyticsResponse } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { HorizontalBarChart } from "@/components/charts/HorizontalBarChart"
import { TrendAreaChart } from "@/components/charts/TrendAreaChart"

function sorted(buckets: { label: string; count: number }[]) {
  return [...buckets].sort((a, b) => b.count - a.count)
}

export default function Analytics() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => apiFetch<AnalyticsResponse>("/analytics"),
  })

  if (isLoading || !data) {
    return <p className="text-sm text-muted-foreground">Loading analytics...</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Real counts from your lead database and outreach activity.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Messages sent
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{data.messages_sent}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Messages failed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{data.messages_failed}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Replies</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{data.replies}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Leads discovered over time</CardTitle>
        </CardHeader>
        <CardContent>
          <TrendAreaChart data={data.leads_over_time} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Leads by city</CardTitle>
          </CardHeader>
          <CardContent>
            <HorizontalBarChart data={sorted(data.by_city)} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Leads by category</CardTitle>
          </CardHeader>
          <CardContent>
            <HorizontalBarChart data={sorted(data.by_category)} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Website status</CardTitle>
          </CardHeader>
          <CardContent>
            <HorizontalBarChart data={sorted(data.by_website_status)} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Lead status</CardTitle>
          </CardHeader>
          <CardContent>
            <HorizontalBarChart data={sorted(data.by_status)} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
