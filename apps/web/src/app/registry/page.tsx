"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

interface RegistryPack {
  id: string;
  name: string;
  slug: string;
  summary: string | null;
  difficulty: string | null;
  install_count: number;
  scenario_tags: string[];
  tool_tags: string[];
  provenance: { author_name?: string };
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  intermediate: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  advanced: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  expert: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function RegistryPage() {
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [sort, setSort] = useState("newest");

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchInput), 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["registry", debouncedSearch, difficulty, sort],
    queryFn: () => {
      const params = new URLSearchParams();
      if (debouncedSearch) params.set("search", debouncedSearch);
      if (difficulty) params.set("difficulty", difficulty);
      params.set("sort", sort);
      return api<{ data: RegistryPack[]; meta: { total: number } }>(
        `/registry/packs?${params.toString()}`,
      );
    },
  });

  const packs = data?.data ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold">Skill Pack Registry</h1>
        <p className="mt-2 text-lg text-[hsl(var(--muted-foreground))]">
          Discover and install curated training packs for your organization.
        </p>
      </div>

      {isError && (
        <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
          Failed to load packs. Please try again.
        </div>
      )}

      <div className="mb-6 flex flex-wrap gap-3">
        <Input
          placeholder="Search packs..."
          aria-label="Search skill packs"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="max-w-xs"
        />
        <label className="sr-only" htmlFor="difficulty-filter">Difficulty</label>
        <select
          id="difficulty-filter"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          className="rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="">All levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
          <option value="expert">Expert</option>
        </select>
        <label className="sr-only" htmlFor="sort-select">Sort</label>
        <select
          id="sort-select"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="newest">Newest</option>
          <option value="popular">Most installed</option>
          <option value="name">Name A-Z</option>
        </select>
      </div>

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}

      {!isLoading && packs.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No packs found matching your criteria.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" role="list">
        {packs.map((pack) => (
          <Link
            key={pack.id}
            href={`/registry/${pack.id}`}
            aria-label={pack.name}
            className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
          >
            <div className="flex items-start justify-between">
              <h3 className="font-semibold group-hover:text-[hsl(var(--primary))]">
                {pack.name}
              </h3>
              {pack.difficulty && (
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${DIFFICULTY_COLORS[pack.difficulty] ?? ""}`}
                >
                  {pack.difficulty}
                </span>
              )}
            </div>
            {pack.summary && (
              <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
                {pack.summary}
              </p>
            )}
            <div className="mt-3 flex items-center justify-between text-xs text-[hsl(var(--muted-foreground))]">
              <span>{pack.provenance?.author_name ?? "Unknown author"}</span>
              <span>{pack.install_count} installs</span>
            </div>
            {pack.scenario_tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {pack.scenario_tags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </Link>
        ))}
      </div>

      {data?.meta && packs.length < data.meta.total && (
        <p className="mt-6 text-center text-sm text-[hsl(var(--muted-foreground))]">
          Showing {packs.length} of {data.meta.total} packs
        </p>
      )}
    </div>
  );
}
