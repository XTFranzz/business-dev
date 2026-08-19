interface ChartTooltipProps {
  active?: boolean
  payload?: { value: number; payload: { label: string } }[]
  label?: string
}

export function ChartTooltip({ active, payload }: ChartTooltipProps) {
  if (!active || !payload || payload.length === 0) return null
  const entry = payload[0]

  return (
    <div
      className="rounded-md border px-3 py-2 text-xs shadow-sm"
      style={{ background: "var(--chart-surface)", borderColor: "var(--chart-grid)" }}
    >
      <p style={{ color: "var(--chart-ink-secondary)" }}>{entry.payload.label}</p>
      <p className="font-medium" style={{ color: "var(--chart-series-1)" }}>
        {entry.value.toLocaleString()}
      </p>
    </div>
  )
}
