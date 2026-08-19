import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link, useNavigate } from "react-router-dom"
import { apiFetch } from "@/lib/api"
import type { CampaignDetail, CampaignRead, MessageTemplateRead } from "@/types/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function Campaigns() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [name, setName] = useState("")
  const [templateId, setTemplateId] = useState("")
  const [city, setCity] = useState("")
  const [category, setCategory] = useState("")
  const [hasWebsite, setHasWebsite] = useState("false")
  const [dailyLimit, setDailyLimit] = useState(20)

  const { data: campaigns } = useQuery({
    queryKey: ["campaigns"],
    queryFn: () => apiFetch<CampaignRead[]>("/campaigns"),
  })

  const { data: templates } = useQuery({
    queryKey: ["templates"],
    queryFn: () => apiFetch<MessageTemplateRead[]>("/message-templates"),
  })

  const createCampaign = useMutation({
    mutationFn: () =>
      apiFetch<CampaignDetail>("/campaigns", {
        method: "POST",
        body: JSON.stringify({
          name,
          template_id: templateId,
          city: city || null,
          category: category || null,
          has_website: hasWebsite === "any" ? null : hasWebsite === "true",
          daily_send_limit: dailyLimit,
        }),
      }),
    onSuccess: (campaign) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] })
      navigate(`/campaigns/${campaign.id}`)
    },
  })

  const deleteCampaign = useMutation({
    mutationFn: (id: string) => apiFetch<void>(`/campaigns/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] }),
  })

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Campaigns</h1>
        <p className="text-sm text-muted-foreground">
          Build an outreach audience from your leads, review generated messages, then send.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">New campaign</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="c-name">Campaign name</Label>
            <Input id="c-name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>Template</Label>
            <Select value={templateId} onValueChange={setTemplateId}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a template" />
              </SelectTrigger>
              <SelectContent>
                {templates?.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {templates?.length === 0 && (
              <p className="text-xs text-muted-foreground">
                No templates yet — create one on the Templates page first.
              </p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="c-city">City</Label>
              <Input id="c-city" value={city} onChange={(e) => setCity(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-category">Category</Label>
              <Input
                id="c-category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Website</Label>
              <Select value={hasWebsite} onValueChange={setHasWebsite}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="any">Any</SelectItem>
                  <SelectItem value="false">No website</SelectItem>
                  <SelectItem value="true">Has website</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c-limit">Daily send limit</Label>
              <Input
                id="c-limit"
                type="number"
                min={1}
                max={500}
                value={dailyLimit}
                onChange={(e) => setDailyLimit(Number(e.target.value))}
              />
            </div>
          </div>
          <Button
            onClick={() => createCampaign.mutate()}
            disabled={!name || !templateId || createCampaign.isPending}
          >
            {createCampaign.isPending ? "Building audience..." : "Create campaign"}
          </Button>
          {createCampaign.isError && (
            <p className="text-sm text-destructive">{(createCampaign.error as Error).message}</p>
          )}
        </CardContent>
      </Card>

      <div className="space-y-3">
        {campaigns?.length === 0 && (
          <p className="text-sm text-muted-foreground">No campaigns yet.</p>
        )}
        {campaigns?.map((c) => (
          <Card key={c.id} className="transition-colors hover:bg-accent/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <Link to={`/campaigns/${c.id}`} className="flex-1">
                <CardTitle className="text-base">{c.name}</CardTitle>
              </Link>
              <div className="flex items-center gap-2">
                <Badge variant="outline">{c.status}</Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteCampaign.mutate(c.id)}
                  disabled={deleteCampaign.isPending}
                >
                  Delete
                </Button>
              </div>
            </CardHeader>
            <Link to={`/campaigns/${c.id}`}>
              <CardContent className="flex gap-4 text-sm text-muted-foreground">
                <span>{c.lead_count} leads</span>
                <span>{c.pending_approval_count} pending approval</span>
                <span>{c.approved_count} approved</span>
                <span>{c.sent_count} sent</span>
                {c.failed_count > 0 && <span>{c.failed_count} failed</span>}
              </CardContent>
            </Link>
          </Card>
        ))}
      </div>
    </div>
  )
}
