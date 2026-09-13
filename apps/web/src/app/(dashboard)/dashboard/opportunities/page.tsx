"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Opportunity {
  id: string;
  employer_org_id: string;
  title: string;
  description: string | null;
  opportunity_type: string;
  location_mode: string | null;
  location_text: string | null;
  compensation_display: string | null;
  required_capabilities: { capability_id: string; min_level: number; capability_name?: string }[];
  preferred_capabilities: { capability_id: string; min_level: number; capability_name?: string }[];
  application_deadline: string | null;
  openings: number;
  status: string;
  created_at: string;
}

interface PaginatedResponse {
  data: Opportunity[];
  meta: { total: number; page: number; per_page: number; has_more: boolean };
}

const TYPE_OPTIONS = [
  { value: "", label: "All types" },
  { value: "internship", label: "Internship" },
  { value: "full_time", label: "Full-time" },
  { value: "part_time", label: "Part-time" },
  { value: "contract", label: "Contract" },
  { value: "freelance", label: "Freelance" },
  { value: "project_role", label: "Project role" },
  { value: "apprenticeship", label: "Apprenticeship" },
  { value: "campus_project", label: "Campus project" },
];

const TYPE_COLORS: Record<string, string> = {
  internship: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  full_time: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  part_time: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200",
  contract: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  freelance: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  project_role: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  apprenticeship: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
  campus_project: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
};

const LOCATION_ICONS: Record<string, string> = {
  remote: "🌍",
  onsite: "🏢",
  hybrid: "🔄",
};

export default function OpportunitiesPage() {
  const [typeFilter, setTypeFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["opportunities", typeFilter, page],
    queryFn: () => {
      const params = new URLSearchParams({ status: "open", page: String(page), per_page: "12" });
      if (typeFilter) params.set("opportunity_type", typeFilter);
      return apiWithAuth<PaginatedResponse>(`/talent/opportunities?${params}`);
    },
  });

  const opportunities = data?.data ?? [];
  const meta = data?.meta;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Opportunities</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Browse open internships, jobs, and project roles matched to your skills.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setPage(1);
          }}
          className="rounded-md border bg-[hsl(var(--card))] px-3 py-2 text-sm"
        >
          {TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {meta && (
          <span className="text-sm text-[hsl(var(--muted-foreground))]">
            {meta.total} opportunit{meta.total === 1 ? "y" : "ies"} found
          </span>
        )}
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-52 animate-pulse rounded-lg border bg-[hsl(var(--card))]" />
          ))}
        </div>
      ) : opportunities.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
          <p className="text-lg font-medium">No opportunities found</p>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {typeFilter ? "Try adjusting your filters." : "Check back later for new openings."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {opportunities.map((opp) => (
            <OpportunityCard key={opp.id} opportunity={opp} />
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

function OpportunityCard({ opportunity: opp }: { opportunity: Opportunity }) {
  const typeColor = TYPE_COLORS[opp.opportunity_type] ?? "bg-gray-100 text-gray-800";
  const locationIcon = LOCATION_ICONS[opp.location_mode ?? ""] ?? "";
  const deadline = opp.application_deadline ? new Date(opp.application_deadline) : null;
  const isExpiring = deadline && deadline.getTime() - Date.now() < 7 * 24 * 60 * 60 * 1000;

  return (
    <Link
      href={`/dashboard/opportunities/${opp.id}`}
      className="group flex flex-col rounded-lg border bg-[hsl(var(--card))] p-5 transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold leading-tight group-hover:underline">{opp.title}</h3>
        <span className={cn("shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium", typeColor)}>
          {opp.opportunity_type.replace(/_/g, " ")}
        </span>
      </div>

      {(opp.location_mode || opp.location_text) && (
        <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
          {locationIcon} {opp.location_text ?? opp.location_mode}
        </p>
      )}

      {opp.compensation_display && (
        <p className="mt-1 text-sm font-medium">{opp.compensation_display}</p>
      )}

      {/* Required capabilities */}
      {opp.required_capabilities.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {opp.required_capabilities.slice(0, 4).map((cap, i) => (
            <span key={i} className="rounded-md bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
              {cap.capability_name ?? cap.capability_id} ≥ L{cap.min_level}
            </span>
          ))}
          {opp.required_capabilities.length > 4 && (
            <span className="rounded-md bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
              +{opp.required_capabilities.length - 4} more
            </span>
          )}
        </div>
      )}

      <div className="mt-auto pt-3">
        {deadline && (
          <p
            className={cn(
              "text-xs",
              isExpiring
                ? "font-medium text-red-600 dark:text-red-400"
                : "text-[hsl(var(--muted-foreground))]",
            )}
          >
            {isExpiring ? "⏰ " : ""}Deadline:{" "}
            {deadline.toLocaleDateString(undefined, {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </p>
        )}
        {opp.openings > 1 && (
          <p className="text-xs text-[hsl(var(--muted-foreground))]">{opp.openings} openings</p>
        )}
      </div>
    </Link>
  );
}
