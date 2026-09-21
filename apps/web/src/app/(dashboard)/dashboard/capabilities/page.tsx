"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface Capability {
  id: string;
  canonical_name: string;
  category: string;
  status: string;
  slug: string;
  parent_id: string | null;
}

export default function CapabilitiesAdminPage() {
  const [category, setCategory] = useState<string>("");
  const { data, isLoading, isError } = useQuery({
    queryKey: ["capabilities", category],
    queryFn: () =>
      api<{ data: Capability[]; meta: { total: number } }>(
        `/api/v1/talent/capabilities${category ? `?category=${category}` : ""}`,
      ),
  });

  const capabilities = data?.data ?? [];
  const total = (data as { meta?: { total: number } })?.meta?.total ?? capabilities.length;

  if (isError) return <div className="p-8 text-center text-red-600">Failed to load data</div>;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Capability Taxonomy</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{total} capabilities</p>
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-md border bg-[hsl(var(--background))] px-3 py-2 text-sm"
        >
          <option value="">All Categories</option>
          <option value="skill">Skill</option>
          <option value="design">Design</option>
          <option value="ai">AI</option>
          <option value="engineering">Engineering</option>
          <option value="production">Production</option>
          <option value="business">Business</option>
        </select>
      </div>

      {isLoading ? (
        <div className="text-[hsl(var(--muted-foreground))]">Loading capabilities…</div>
      ) : capabilities.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center shadow-sm">
          <div className="mb-4 text-4xl">🧠</div>
          <p className="text-[hsl(var(--muted-foreground))]">
            No capabilities found. Import a taxonomy to get started.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border shadow-sm">
          <table className="w-full">
            <thead className="bg-[hsl(var(--secondary))]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Category</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Slug</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {capabilities.map((cap) => (
                <tr key={cap.id} className="bg-[hsl(var(--card))]">
                  <td className="px-4 py-3 text-sm font-medium">{cap.canonical_name}</td>
                  <td className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                    {cap.category}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${cap.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}
                    >
                      {cap.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-[hsl(var(--muted-foreground))]">
                    {cap.slug}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
