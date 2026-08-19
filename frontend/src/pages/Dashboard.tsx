import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "@/lib/api"
import type { DashboardStats } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const STAT_FIELDS: { key: keyof DashboardStats; label: string }[] = [
  { key: "total_leads", label: "Total Leads" },
  { key: "new_leads", label: "New Leads" },
  { key: "no_website", label: "No Website" },
  { key: "high_opportunity", label: "High Opportunity" },
  { key: "contacted", label: "Contacted" },
  { key: "replied", label: "Replied" },
  { key: "interested", label: "Interested" },
  { key: "converted", label: "Converted" },
]

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => apiFetch<DashboardStats>("/dashboard/stats"),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Overview of your lead pipeline.</p>
      </div>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {STAT_FIELDS.map(({ key, label }) => (
          <Card key={key}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-semibold">
                {isLoading || !data ? "—" : data[key]}
              </span>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
