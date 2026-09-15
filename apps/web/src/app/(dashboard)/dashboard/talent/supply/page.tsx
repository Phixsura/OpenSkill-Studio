"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";
import { cn } from "@/lib/utils";

interface SupplyItem {
  capability_id: string;
  capability_name: string;
  category: string;
  total_supply: number;
}

const CATEGORIES = [
  { value: "", label: "All categories" },
  { value: "visual_design", label: "Visual Design" },
  { value: "production", label: "Production" },
  { value: "communication", label: "Communication" },
  { value: "workflow_design", label: "Workflow Design" },
  { value: "ai_fundamentals", label: "AI Fundamentals" },
  { value: "business", label: "Business" },
];

export default function SupplyPage() {
  const [category, setCategory] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["talent-supply", category],
    queryFn: () => {
      const params = new URLSearchParams({ limit: "100" });
      if (category) params.set("category", category);
      return apiWithAuth<{ data: SupplyItem[] }>(
        `/talent/intelligence/supply?${params.toString()}`,
      );
    },
  });

  const items = data?.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/dashboard/talent"
          className="text-sm text-[hsl(var(--muted-foreground))] hover:underline"
        >
          ← Talent Intelligence
        </Link>
        <h1 className="mt-2 text-3xl font-bold">Verified Supply</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Discoverable talent with verified evidence, aggregated by capability
        </p>
      </div>

      {/* Filter */}
      <div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-md border bg-[hsl(var(--card))] px-3 py-2 text-sm"
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-10 animate-pulse rounded bg-[hsl(var(--muted))]" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
          No supply data available{category ? ` for ${category.replace(/_/g, " ")}` : ""}. Supply
          counts below the privacy threshold are suppressed.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-[hsl(var(--muted))]/50 text-left">
                <th className="px-4 py-3 font-medium">Capability</th>
                <th className="px-4 py-3 font-medium">Category</th>
                <th className="px-4 py-3 text-right font-medium">Verified Supply</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => (
                <tr
                  key={item.capability_id}
                  className={cn(
                    "border-b last:border-0",
                    i % 2 === 1 && "bg-[hsl(var(--muted))]/20",
                  )}
                >
                  <td className="px-4 py-3 font-medium">{item.capability_name}</td>
                  <td className="px-4 py-3 capitalize text-[hsl(var(--muted-foreground))]">
                    {item.category.replace(/_/g, " ")}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">{item.total_supply}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-[hsl(var(--muted-foreground))]">
        Counts below the minimum cohort threshold are suppressed to prevent individual
        re-identification.
      </p>
    </div>
  );
}
