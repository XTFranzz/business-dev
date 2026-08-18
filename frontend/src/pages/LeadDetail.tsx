import { useParams } from "react-router-dom"

export default function LeadDetail() {
  const { id } = useParams()

  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold tracking-tight">Lead {id}</h1>
      <p className="text-sm text-muted-foreground">
        The lead detail profile will appear here once the leads API is built (Phase 1,
        increments 8–10).
      </p>
    </div>
  )
}
