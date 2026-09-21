"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

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

interface CursorResponse {
  data: Opportunity[];
  meta: { next_cursor: string | null; has_more: boolean };
}

interface Bookmark {
  id: string;
  entity_type: string;
  entity_id: string;
}

interface Application {
  id: string;
  opportunity_id: string;
  status: string;
}

interface SavedSearch {
  id: string;
  name: string;
  criteria: Record<string, string>;
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

const LOCATION_OPTIONS = [
  { value: "", label: "All locations" },
  { value: "remote", label: "🌍 Remote" },
  { value: "hybrid", label: "🔄 Hybrid" },
  { value: "onsite", label: "🏢 On-site" },
];

const SORT_OPTIONS = [
  { value: "newest", label: "Newest first" },
  { value: "deadline", label: "Closing soon" },
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
  const queryClient = useQueryClient();
  const [typeFilter, setTypeFilter] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [cursor, setCursor] = useState<string | null>(null);
  const [cursorStack, setCursorStack] = useState<(string | null)[]>([]);
  const [showSaveSearch, setShowSaveSearch] = useState(false);
  const [saveSearchName, setSaveSearchName] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounce search query (300ms)
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(searchQuery);
      setCursor(null);
      setCursorStack([]);
    }, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [searchQuery]);

  // Fetch opportunities
  const { data, isLoading, isError } = useQuery({
    queryKey: ["opportunities", typeFilter, locationFilter, sortBy, debouncedQuery, cursor],
    queryFn: () => {
      const params = new URLSearchParams({ status: "open", limit: "12" });
      if (typeFilter) params.set("opportunity_type", typeFilter);
      if (locationFilter) params.set("location_mode", locationFilter);
      if (sortBy) params.set("sort", sortBy);
      if (debouncedQuery.trim()) params.set("q", debouncedQuery.trim());
      if (cursor) params.set("cursor", cursor);
      return apiWithAuth<CursorResponse>(`/talent/opportunities?${params}`);
    },
  });

  // Fetch user's bookmarks
  const { data: bookmarksData } = useQuery({
    queryKey: ["bookmarks"],
    queryFn: () => apiWithAuth<{ data: Bookmark[] }>("/talent/bookmarks"),
  });
  const bookmarkedIds = useMemo(() => {
    const ids = new Set<string>();
    bookmarksData?.data?.forEach((b: Bookmark) => {
      if (b.entity_type === "opportunity") ids.add(b.entity_id);
    });
    return ids;
  }, [bookmarksData]);

  // Fetch user's applications to show "Applied" state
  const { data: applicationsData } = useQuery({
    queryKey: ["my-applications"],
    queryFn: () => apiWithAuth<{ data: Application[] }>("/talent/applications?limit=200"),
  });
  const appliedOppIds = useMemo(() => {
    const ids = new Set<string>();
    applicationsData?.data?.forEach((a: Application) => ids.add(a.opportunity_id));
    return ids;
  }, [applicationsData]);

  // Fetch saved searches
  const { data: savedSearchesData } = useQuery({
    queryKey: ["saved-searches"],
    queryFn: () =>
      apiWithAuth<{ data: SavedSearch[] }>("/talent/saved-searches").catch(() => ({ data: [] })),
  });

  // Bookmark mutation
  const bookmarkMutation = useMutation({
    mutationFn: (oppId: string) =>
      apiWithAuth("/talent/bookmarks", {
        method: "POST",
        body: JSON.stringify({ entity_type: "opportunity", entity_id: oppId }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bookmarks"] }),
  });

  // Unbookmark mutation
  const unbookmarkMutation = useMutation({
    mutationFn: (bookmarkId: string) =>
      apiWithAuth(`/talent/bookmarks/${bookmarkId}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bookmarks"] }),
  });

  // Apply mutation
  const applyMutation = useMutation({
    mutationFn: (oppId: string) =>
      apiWithAuth("/talent/applications", {
        method: "POST",
        body: JSON.stringify({ opportunity_id: oppId }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-applications"] }),
  });

  // Save search mutation
  const saveSearchMutation = useMutation({
    mutationFn: (name: string) =>
      apiWithAuth("/talent/saved-searches", {
        method: "POST",
        body: JSON.stringify({
          name,
          criteria: {
            q: debouncedQuery,
            opportunity_type: typeFilter,
            location_mode: locationFilter,
            sort: sortBy,
          },
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-searches"] });
      setShowSaveSearch(false);
      setSaveSearchName("");
    },
  });

  const handleToggleBookmark = (oppId: string) => {
    const existing = bookmarksData?.data?.find(
      (b: Bookmark) => b.entity_type === "opportunity" && b.entity_id === oppId,
    );
    if (existing) {
      unbookmarkMutation.mutate(existing.id);
    } else {
      bookmarkMutation.mutate(oppId);
    }
  };

  const handleApply = (oppId: string) => {
    applyMutation.mutate(oppId);
  };

  const handleRestoreSavedSearch = (search: SavedSearch) => {
    const c = search.criteria ?? {};
    setSearchQuery(c.q ?? "");
    setTypeFilter(c.opportunity_type ?? "");
    setLocationFilter(c.location_mode ?? "");
    setSortBy(c.sort ?? "newest");
    setCursor(null);
    setCursorStack([]);
  };

  const filtered = data?.data ?? [];
  const meta = data?.meta;

  const resetFilters = () => {
    setTypeFilter("");
    setLocationFilter("");
    setSortBy("newest");
    setSearchQuery("");
    setCursor(null);
    setCursorStack([]);
  };

  if (isError) return <div className="p-8 text-center text-red-600">Failed to load data</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Opportunities</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Browse open internships, jobs, and project roles matched to your skills.
        </p>
      </div>

      {/* Search & Filters */}
      <div className="space-y-3">
        {/* Search input */}
        <div className="relative">
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[hsl(var(--muted-foreground))]">
            🔍
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by title or description…"
            className="w-full rounded-md border bg-[hsl(var(--card))] py-2.5 pl-9 pr-3 text-sm placeholder:text-[hsl(var(--muted-foreground))]"
          />
        </div>

        {/* Filter row */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value);
              setCursor(null);
              setCursorStack([]);
            }}
            className="rounded-md border bg-[hsl(var(--card))] px-3 py-2 text-sm"
          >
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <select
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            className="rounded-md border bg-[hsl(var(--card))] px-3 py-2 text-sm"
          >
            {LOCATION_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-md border bg-[hsl(var(--card))] px-3 py-2 text-sm"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {(typeFilter || locationFilter || searchQuery) && (
            <button
              onClick={resetFilters}
              className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            >
              Clear filters
            </button>
          )}

          {/* Save Search */}
          <button
            onClick={() => setShowSaveSearch(!showSaveSearch)}
            className="text-sm text-[hsl(var(--primary))] hover:underline"
            title="Save current search"
          >
            💾 Save search
          </button>

          {/* Saved Searches dropdown */}
          {savedSearchesData?.data && savedSearchesData.data.length > 0 && (
            <select
              onChange={(e) => {
                const search = savedSearchesData.data.find(
                  (s: SavedSearch) => s.id === e.target.value,
                );
                if (search) handleRestoreSavedSearch(search);
              }}
              value=""
              className="rounded-md border bg-[hsl(var(--card))] px-3 py-2 text-sm"
            >
              <option value="">📂 Saved searches</option>
              {savedSearchesData.data.map((s: SavedSearch) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          )}

          <span className="ml-auto text-sm text-[hsl(var(--muted-foreground))]">
            {filtered.length} result{filtered.length !== 1 ? "s" : ""}
          </span>
        </div>

        {/* Save Search form */}
        {showSaveSearch && (
          <div className="flex items-center gap-2 rounded-md border bg-[hsl(var(--card))] p-3">
            <input
              type="text"
              value={saveSearchName}
              onChange={(e) => setSaveSearchName(e.target.value)}
              placeholder="Name this search…"
              className="flex-1 rounded-md border bg-transparent px-3 py-1.5 text-sm"
            />
            <Button
              size="sm"
              onClick={() => saveSearchName.trim() && saveSearchMutation.mutate(saveSearchName)}
              disabled={!saveSearchName.trim() || saveSearchMutation.isPending}
            >
              {saveSearchMutation.isPending ? "Saving…" : "Save"}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setShowSaveSearch(false)}>
              Cancel
            </Button>
          </div>
        )}
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-52 animate-pulse rounded-lg border bg-[hsl(var(--card))]" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
          <p className="text-4xl">🔍</p>
          <p className="mt-3 text-lg font-medium">No opportunities found</p>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {typeFilter || locationFilter || searchQuery
              ? "Try adjusting your search or filters."
              : "Check back later for new openings."}
          </p>
          {(typeFilter || locationFilter || searchQuery) && (
            <Button variant="outline" className="mt-4" onClick={resetFilters}>
              Clear all filters
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((opp) => (
            <OpportunityCard
              key={opp.id}
              opportunity={opp}
              isBookmarked={bookmarkedIds.has(opp.id)}
              isApplied={appliedOppIds.has(opp.id)}
              onToggleBookmark={() => handleToggleBookmark(opp.id)}
              onApply={() => handleApply(opp.id)}
              applyPending={applyMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Cursor Pagination */}
      {meta && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              const prev = cursorStack[cursorStack.length - 1] ?? null;
              setCursor(prev);
              setCursorStack((s) => s.slice(0, -1));
            }}
            disabled={cursorStack.length === 0 && cursor === null}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (meta.next_cursor) {
                setCursorStack((s) => [...s, cursor]);
                setCursor(meta.next_cursor);
              }
            }}
            disabled={!meta.has_more}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

function OpportunityCard({
  opportunity: opp,
  isBookmarked,
  isApplied,
  onToggleBookmark,
  onApply,
  applyPending,
}: {
  opportunity: Opportunity;
  isBookmarked: boolean;
  isApplied: boolean;
  onToggleBookmark: () => void;
  onApply: () => void;
  applyPending: boolean;
}) {
  const typeColor = TYPE_COLORS[opp.opportunity_type] ?? "bg-gray-100 text-gray-800";
  const locationIcon = LOCATION_ICONS[opp.location_mode ?? ""] ?? "";
  const deadline = opp.application_deadline ? new Date(opp.application_deadline) : null;
  const isExpiring = deadline && deadline.getTime() - Date.now() < 7 * 24 * 60 * 60 * 1000;

  return (
    <div className="group flex flex-col rounded-lg border bg-[hsl(var(--card))] p-5 transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-2">
        <Link
          href={`/dashboard/opportunities/${opp.id}`}
          className="font-semibold leading-tight hover:underline"
        >
          {opp.title}
        </Link>
        <div className="flex shrink-0 items-center gap-1.5">
          {/* Bookmark button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
              onToggleBookmark();
            }}
            className="text-lg transition-transform hover:scale-110"
            title={isBookmarked ? "Remove bookmark" : "Bookmark"}
          >
            {isBookmarked ? "❤️" : "🤍"}
          </button>
          <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", typeColor)}>
            {opp.opportunity_type.replace(/_/g, " ")}
          </span>
        </div>
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

        {/* Apply button */}
        <div className="mt-3">
          {isApplied ? (
            <span className="inline-flex items-center gap-1 rounded-md bg-green-100 px-3 py-1.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
              ✓ Applied
            </span>
          ) : (
            <Button
              size="sm"
              className="w-full"
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                onApply();
              }}
              disabled={applyPending}
            >
              {applyPending ? "Applying…" : "Apply Now"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
