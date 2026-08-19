import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiFetch } from "@/lib/api"
import type { MessageTemplateRead } from "@/types/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const VARIABLE_HINT =
  "Variables: {{business_name}} {{city}} {{category}} {{website_status}} {{social_platform}} {{lead_score}}"

export default function Templates() {
  const queryClient = useQueryClient()
  const [name, setName] = useState("")
  const [subject, setSubject] = useState("")
  const [body, setBody] = useState("")

  const { data: templates } = useQuery({
    queryKey: ["templates"],
    queryFn: () => apiFetch<MessageTemplateRead[]>("/message-templates"),
  })

  const createTemplate = useMutation({
    mutationFn: () =>
      apiFetch<MessageTemplateRead>("/message-templates", {
        method: "POST",
        body: JSON.stringify({ name, subject, body }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] })
      setName("")
      setSubject("")
      setBody("")
    },
  })

  const deleteTemplate = useMutation({
    mutationFn: (id: string) => apiFetch<void>(`/message-templates/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["templates"] }),
  })

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Templates</h1>
        <p className="text-sm text-muted-foreground">
          Reusable outreach message templates. {VARIABLE_HINT}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">New template</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="t-name">Name</Label>
            <Input id="t-name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="t-subject">Subject</Label>
            <Input
              id="t-subject"
              placeholder="Quick idea for {{business_name}}"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="t-body">Body</Label>
            <Textarea
              id="t-body"
              rows={6}
              placeholder="Hi! I came across {{business_name}}..."
              value={body}
              onChange={(e) => setBody(e.target.value)}
            />
          </div>
          <Button
            onClick={() => createTemplate.mutate()}
            disabled={!name || !subject || !body || createTemplate.isPending}
          >
            {createTemplate.isPending ? "Saving..." : "Save template"}
          </Button>
        </CardContent>
      </Card>

      <div className="space-y-3">
        {templates?.length === 0 && (
          <p className="text-sm text-muted-foreground">No templates yet.</p>
        )}
        {templates?.map((t) => (
          <Card key={t.id}>
            <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
              <CardTitle className="text-base">{t.name}</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteTemplate.mutate(t.id)}
                disabled={deleteTemplate.isPending}
              >
                Delete
              </Button>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              <p className="font-medium">{t.subject}</p>
              <p className="whitespace-pre-wrap text-muted-foreground">{t.body}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
