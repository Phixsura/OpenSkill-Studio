"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function BookmarksPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["talent-bookmarks"],
    queryFn: () =>
      api<{ data: { id: string; opportunity_id: string; notes: string | null }[] }>(
        "/api/v1/talent/bookmarks",
      ),
    retry: false,
  });

  const items = data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Saved Opportunities</h1>
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading…</div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center shadow-sm">
          <div className="mb-4 text-4xl">🔖</div>
          <p className="text-[hsl(var(--muted-foreground))]">
            No saved opportunities yet. Bookmark opportunities you&apos;re interested in.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
              <p className="font-medium">Opportunity {item.opportunity_id}</p>
              {item.notes && (
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{item.notes}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
