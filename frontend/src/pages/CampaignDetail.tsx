import { useState } from "react"
import { useParams } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { apiFetch } from "@/lib/api"
import type {
  CampaignDetail as CampaignDetailType,
  CampaignLeadRead,
  CampaignProcessResult,
  CampaignStatus,
  MessageRead,
} from "@/types/api"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const STATUS_OPTIONS: CampaignStatus[] = ["draft", "active", "paused", "completed"]

function CampaignLeadCard({ campaignLead }: { campaignLead: CampaignLeadRead }) {
  const queryClient = useQueryClient()
  const message = campaignLead.message
  const [body, setBody] = useState(message?.body ?? "")
  const [subject, setSubject] = useState(message?.subject ?? "")

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["campaign"] })

  const saveEdit = useMutation({
    mutationFn: () =>
      apiFetch<MessageRead>(`/messages/${message?.id}`, {
        method: "PATCH",
        body: JSON.stringify({ subject, body }),
      }),
    onSuccess: invalidate,
  })

  const approve = useMutation({
    mutationFn: () => apiFetch<MessageRead>(`/messages/${message?.id}/approve`, { method: "POST" }),
    onSuccess: invalidate,
  })

  const skip = useMutation({
    mutationFn: () => apiFetch<MessageRead>(`/messages/${message?.id}/skip`, { method: "POST" }),
    onSuccess: invalidate,
  })

  const markReplied = useMutation({
    mutationFn: () =>
      apiFetch<MessageRead>(`/messages/${message?.id}/mark-replied`, { method: "POST" }),
    onSuccess: invalidate,
  })

  if (!message) return null

  const editable = message.status === "draft" || message.status === "pending_approval"
  const dirty = subject !== message.subject || body !== message.body

  function copyMessage() {
    navigator.clipboard.writeText(`${subject}\n\n${body}`)
    toast.success("Message copied to clipboard")
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">{campaignLead.business_name}</CardTitle>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{message.channel === "email" ? "Email" : "Manual copy"}</Badge>
          <Badge variant="outline">{campaignLead.status}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {editable ? (
          <>
            <Input
              className="font-medium"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
            <Textarea rows={4} value={body} onChange={(e) => setBody(e.target.value)} />
          </>
        ) : (
          <>
            <p className="text-sm font-medium">{message.subject}</p>
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">{message.body}</p>
          </>
        )}

        <div className="flex flex-wrap gap-2">
          {editable && dirty && (
            <Button size="sm" variant="outline" onClick={() => saveEdit.mutate()}>
              Save edit
            </Button>
          )}
          {campaignLead.status === "pending" && (
            <>
              <Button size="sm" onClick={() => approve.mutate()}>
                Approve
              </Button>
              <Button size="sm" variant="ghost" onClick={() => skip.mutate()}>
                Skip
              </Button>
            </>
          )}
          {message.channel === "manual_copy" && (
            <Button size="sm" variant="outline" onClick={copyMessage}>
              Copy Message
            </Button>
          )}
          {campaignLead.profile_url && (
            <Button size="sm" variant="outline" asChild>
              <a href={campaignLead.profile_url} target="_blank" rel="noreferrer">
                Open Profile
              </a>
            </Button>
          )}
          {message.status === "sent" && (
            <Button size="sm" variant="ghost" onClick={() => markReplied.mutate()}>
              Mark Replied
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default function CampaignDetail() {
  const { id } = useParams()
  const queryClient = useQueryClient()

  const { data: campaign, isLoading } = useQuery({
    queryKey: ["campaign", id],
    queryFn: () => apiFetch<CampaignDetailType>(`/campaigns/${id}`),
    enabled: !!id,
  })

  const updateStatus = useMutation({
    mutationFn: (status: CampaignStatus) =>
      apiFetch<CampaignDetailType>(`/campaigns/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaign", id] }),
  })

  const processCampaign = useMutation({
    mutationFn: () =>
      apiFetch<CampaignProcessResult>(`/campaigns/${id}/process`, { method: "POST" }),
    onSuccess: (result) => {
      toast.success(`Sent ${result.sent}, failed ${result.failed}, skipped ${result.skipped}`)
      queryClient.invalidateQueries({ queryKey: ["campaign", id] })
    },
    onError: (error: Error) => toast.error(error.message),
  })

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>
  if (!campaign) return null

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{campaign.name}</h1>
          <p className="text-sm text-muted-foreground">
            {campaign.lead_count} leads · daily limit {campaign.daily_send_limit}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={campaign.status}
            onValueChange={(value) => updateStatus.mutate(value as CampaignStatus)}
          >
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {campaign.status === "active" && (
            <Button onClick={() => processCampaign.mutate()} disabled={processCampaign.isPending}>
              {processCampaign.isPending ? "Sending..." : "Send approved batch"}
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Pending approval
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{campaign.pending_approval_count}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Approved</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{campaign.approved_count}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Sent</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{campaign.sent_count}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Failed</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-semibold">{campaign.failed_count}</span>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-3">
        {campaign.leads.map((cl) => (
          <CampaignLeadCard key={cl.id} campaignLead={cl} />
        ))}
      </div>
    </div>
  )
}
