"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function EndorsementsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["talent-endorsements"],
    queryFn: () =>
      api<{
        data: { id: string; capability_id: string; relationship: string; created_at: string }[];
      }>("/api/v1/talent/endorsements"),
    retry: false,
  });

  const { data: summaryData } = useQuery({
    queryKey: ["endorsement-summary"],
    queryFn: () =>
      api<{ data: { total_endorsements: number; by_capability: Record<string, number> } }>(
        "/api/v1/talent/endorsements/summary",
      ),
    retry: false,
  });

  const items = data?.data ?? [];
  const summary = summaryData?.data;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Endorsements</h1>
        {summary && (
          <span className="rounded-full bg-[hsl(var(--primary))] px-3 py-1 text-sm text-white">
            {summary.total_endorsements} total
          </span>
        )}
      </div>
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading…</div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center shadow-sm">
          <div className="mb-4 text-4xl">👍</div>
          <p className="text-[hsl(var(--muted-foreground))]">
            No endorsements yet. Share your profile to get endorsed by peers.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="font-medium">Skill Endorsement</p>
                <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                  {item.relationship}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
