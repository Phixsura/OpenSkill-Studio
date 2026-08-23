"use client";

// Public workflow-pack registry (ADR-010) — sibling family to skill packs.

import { useEffect, useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

// Keep in sync with the seeded platform capabilities
// (apps/api/migrations/versions/f7a81c223001_capability_taxonomy_providers.py)
const CAPABILITY_KEYS = [
  "image_generation",
  "image_editing",
  "image_to_video",
  "text_to_video",
  "video_editing",
  "voice_generation",
  "multimodal_review",
  "upscale",
  "background_removal",
];

interface WorkflowPack {
  id: string;
  name: string;
  summary: string | null;
  workflow_type: string;
  capability_tags: string[];
  scenario_tags: string[];
  install_count: number;
}

const TYPE_COLORS: Record<string, string> = {
  production: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  pipeline: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  review: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
};

export default function WorkflowRegistryPage() {
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [capability, setCapability] = useState("");
  const [workflowType, setWorkflowType] = useState("");
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(1);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(searchInput), 300);
    return () => clearTimeout(t);
  }, [searchInput]);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, capability, workflowType, sort]);

  const { data, isLoading } = useQuery({
    queryKey: ["wf-registry", debouncedSearch, capability, workflowType, sort, page],
    queryFn: () => {
      const params = new URLSearchParams();
      if (debouncedSearch) params.set("search", debouncedSearch);
      if (capability) params.set("capability", capability);
      if (workflowType) params.set("workflow_type", workflowType);
      params.set("sort", sort);
      params.set("page", String(page));
      return api<{ data: WorkflowPack[]; meta: { total: number; has_more: boolean } }>(
        `/registry/workflow-packs?${params.toString()}`,
      );
    },
  });

  const packs = data?.data ?? [];
  const hasMore = data?.meta?.has_more ?? false;

  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold">Registry</h1>
      <p className="mt-1 text-[hsl(var(--muted-foreground))]">
        Reusable AI production workflows — inspect structure and requirements before
        installing.
      </p>

      {/* Family tabs */}
      <div className="mt-6 flex gap-1 border-b">
        <Link
          href="/registry"
          className="rounded-t-md px-4 py-2 text-sm font-medium text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
        >
          Skill Packs
        </Link>
        <Link
          href="/registry/workflows"
          className="rounded-t-md border-b-2 border-[hsl(var(--primary))] px-4 py-2 text-sm font-medium"
          aria-current="page"
        >
          Workflow Packs
        </Link>
      </div>

      {/* Filters */}
      <div className="mt-6 flex flex-wrap gap-3">
        <div className="min-w-[200px] flex-1">
          <label htmlFor="wf-search" className="sr-only">
            Search workflow packs
          </label>
          <Input
            id="wf-search"
            placeholder="Search workflows..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
        </div>
        <label htmlFor="wf-capability" className="sr-only">
          Capability
        </label>
        <select
          id="wf-capability"
          value={capability}
          onChange={(e) => setCapability(e.target.value)}
          className="rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="">All capabilities</option>
          {CAPABILITY_KEYS.map((key) => (
            <option key={key} value={key}>
              {key.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <label htmlFor="wf-type" className="sr-only">
          Workflow type
        </label>
        <select
          id="wf-type"
          value={workflowType}
          onChange={(e) => setWorkflowType(e.target.value)}
          className="rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="">All types</option>
          <option value="production">Production</option>
          <option value="pipeline">Pipeline</option>
          <option value="review">Review</option>
        </select>
        <label htmlFor="wf-sort" className="sr-only">
          Sort
        </label>
        <select
          id="wf-sort"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="newest">Newest</option>
          <option value="most_installed">Most installed</option>
          <option value="name">Name</option>
        </select>
      </div>

      {isLoading && (
        <p className="mt-8 text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}

      {!isLoading && packs.length === 0 && (
        <div className="mt-8 rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No workflow packs found.
        </div>
      )}

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {packs.map((pack) => (
          <Link
            key={pack.id}
            href={`/registry/workflows/${pack.id}`}
            className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
          >
            <div className="flex items-center gap-2">
              <h2 className="truncate font-semibold group-hover:underline">{pack.name}</h2>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${TYPE_COLORS[pack.workflow_type] ?? ""}`}
              >
                {pack.workflow_type}
              </span>
            </div>
            {pack.summary && (
              <p className="mt-2 line-clamp-2 text-sm text-[hsl(var(--muted-foreground))]">
                {pack.summary}
              </p>
            )}
            <div className="mt-3 flex flex-wrap gap-1.5">
              {pack.capability_tags.slice(0, 3).map((cap) => (
                <span
                  key={cap}
                  className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs"
                >
                  {cap.replace(/_/g, " ")}
                </span>
              ))}
            </div>
            <p className="mt-3 text-xs text-[hsl(var(--muted-foreground))]">
              {pack.install_count} install{pack.install_count === 1 ? "" : "s"}
            </p>
          </Link>
        ))}
      </div>

      {(page > 1 || hasMore) && (
        <div className="mt-8 flex items-center justify-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Page {page}</span>
          <Button
            variant="secondary"
            size="sm"
            disabled={!hasMore}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </main>
  );
}
