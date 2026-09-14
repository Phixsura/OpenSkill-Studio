"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function OffersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["talent-offers"],
    queryFn: () =>
      api<{
        data: {
          id: string;
          role_title: string;
          status: string;
          compensation_text: string | null;
        }[];
      }>("/api/v1/talent/offers"),
    retry: false,
  });

  const items = data?.data ?? [];

  const statusColors: Record<string, string> = {
    draft: "bg-gray-100 text-gray-700",
    sent: "bg-blue-100 text-blue-700",
    accepted: "bg-green-100 text-green-700",
    declined: "bg-red-100 text-red-700",
    expired: "bg-yellow-100 text-yellow-700",
  };

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">My Offers</h1>
      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading…</div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center shadow-sm">
          <div className="mb-4 text-4xl">📄</div>
          <p className="text-[hsl(var(--muted-foreground))]">No offers yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{item.role_title}</p>
                  {item.compensation_text && (
                    <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                      {item.compensation_text}
                    </p>
                  )}
                </div>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[item.status] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {item.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
