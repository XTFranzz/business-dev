import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const STATS = [
  "Total Leads",
  "New Leads",
  "No Website",
  "High Opportunity",
  "Contacted",
  "Replied",
  "Interested",
  "Converted",
]

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Overview of your lead pipeline. Stats populate once discovery is wired up.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {STATS.map((label) => (
          <Card key={label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-semibold">—</span>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
