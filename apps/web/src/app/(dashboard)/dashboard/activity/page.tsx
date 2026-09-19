"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function ActivityPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["talent-activity"],
    queryFn: () =>
      api<{ data: { action_type: string; target_type: string; created_at: string }[] }>(
        "/api/v1/talent/activity",
      ),
    retry: false,
  });

  const items = data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Activity Log</h1>
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading…</div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center shadow-sm">
          <div className="mb-4 text-4xl">📋</div>
          <p className="text-[hsl(var(--muted-foreground))]">No activity yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item, i) => (
            <div key={i} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="font-medium">{item.action_type}</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">{item.target_type}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
