import { useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { apiFetch } from "@/lib/api"
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

export default function Leads() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["leads"],
    queryFn: () => apiFetch<BusinessListResponse>("/leads?limit=100"),
  })

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Leads</h1>
        <p className="text-sm text-muted-foreground">
          {data ? `${data.count} businesses discovered` : "Loading..."}
        </p>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading leads...</p>}
      {isError && <p className="text-sm text-destructive">{(error as Error).message}</p>}

      {data && data.results.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No leads yet — run a search from Discover to populate this list.
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
