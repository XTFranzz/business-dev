import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"

export default function Messages() {
  return (
    <div className="space-y-3">
      <h1 className="text-2xl font-semibold tracking-tight">Messages</h1>
      <p className="max-w-lg text-sm text-muted-foreground">
        There's no separate inbox here — generated messages live inside each campaign. Open a
        campaign to review, edit, and approve messages per lead: emailed leads send via Gmail,
        and leads reachable only by phone/social get a "Copy Message" + "Open Profile" button
        for you to send manually.
      </p>
      <Button asChild variant="outline">
        <Link to="/campaigns">Go to Campaigns</Link>
      </Button>
    </div>
  )
}
