"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Application {
  id: string;
  opportunity_id: string;
  user_id: string;
  status: string;
  cover_note: string | null;
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse {
  data: Application[];
  meta: { total: number; page: number; per_page: number; has_more: boolean };
}

const STATUS_TABS = [
  { value: "", label: "All" },
  { value: "submitted", label: "Submitted" },
  { value: "screening", label: "Screening" },
  { value: "interview", label: "Interview" },
  { value: "offer", label: "Offer" },
  { value: "hired", label: "Hired" },
  { value: "rejected", label: "Rejected" },
  { value: "withdrawn", label: "Withdrawn" },
];

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  submitted: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  screening: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  interview: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  assessment: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  offer: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  accepted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  withdrawn: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  hired: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  completed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
};

const STATUS_ICONS: Record<string, string> = {
  submitted: "📤",
  screening: "🔍",
  interview: "🎤",
  assessment: "📝",
  offer: "🎉",
  accepted: "✅",
  rejected: "❌",
  withdrawn: "↩️",
  hired: "🏆",
  completed: "🎓",
};

export default function ApplicationsPage() {
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["my-applications", statusFilter, page],
    queryFn: () => {
      const params = new URLSearchParams({ page: String(page), per_page: "20" });
      if (statusFilter) params.set("status", statusFilter);
      return apiWithAuth<PaginatedResponse>(`/talent/applications?${params}`);
    },
  });

  const applications = data?.data ?? [];
  const meta = data?.meta;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">My Applications</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Track the status of your opportunity applications.
        </p>
      </div>

      {/* Status tabs */}
      <div className="flex flex-wrap gap-1.5 border-b pb-3">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => {
              setStatusFilter(tab.value);
              setPage(1);
            }}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm transition-colors",
              statusFilter === tab.value
                ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                : "hover:bg-[hsl(var(--secondary))]",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Applications list */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg border bg-[hsl(var(--card))]" />
          ))}
        </div>
      ) : applications.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
          <p className="text-lg font-medium">No applications found</p>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {statusFilter
              ? "No applications with this status."
              : "Browse opportunities to get started."}
          </p>
          <Link href="/dashboard/opportunities">
            <Button className="mt-4">Browse Opportunities</Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app) => (
            <ApplicationCard key={app.id} application={app} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {meta && meta.total > meta.per_page && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            Previous
          </Button>
          <span className="text-sm text-[hsl(var(--muted-foreground))]">
            Page {page} of {Math.ceil(meta.total / meta.per_page)}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={!meta.has_more}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

function ApplicationCard({ application: app }: { application: Application }) {
  const statusColor = STATUS_COLORS[app.status] ?? "bg-gray-100 text-gray-800";
  const statusIcon = STATUS_ICONS[app.status] ?? "📋";
  const createdDate = new Date(app.created_at);

  return (
    <Link
      href={`/dashboard/opportunities/${app.opportunity_id}`}
      className="group flex items-center justify-between rounded-lg border bg-[hsl(var(--card))] p-5 transition-shadow hover:shadow-md"
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-3">
          <span className="text-lg">{statusIcon}</span>
          <div className="min-w-0">
            <p className="font-medium group-hover:underline">
              Opportunity {app.opportunity_id.slice(0, 8)}…
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Applied{" "}
              {createdDate.toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </p>
          </div>
        </div>
      </div>
      <span className={cn("shrink-0 rounded-full px-3 py-1 text-xs font-medium", statusColor)}>
        {app.status}
      </span>
    </Link>
  );
}
