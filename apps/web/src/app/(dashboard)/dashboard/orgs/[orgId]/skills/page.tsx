"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth } from "@/lib/api";

interface SkillItem {
  id: string;
  name: string;
  slug: string;
  description: string;
  difficulty: string;
  tags: string[];
  status: string;
  sort_order: number;
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  intermediate: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  advanced: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  expert: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

interface CohortItem {
  id: string;
  name: string;
}

export default function SkillsListPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [cohortFilter, setCohortFilter] = useState("");

  const { data: cohortsData } = useQuery({
    queryKey: ["my-cohorts-skills", orgId],
    queryFn: () =>
      apiWithAuth<{ data: CohortItem[] }>(`/orgs/${orgId}/my-cohorts`),
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: ["skills", orgId, search, difficulty, cohortFilter],
    queryFn: () => {
      const params = new URLSearchParams();
      if (search) params.set("q", search);
      if (difficulty) params.set("difficulty", difficulty);
      if (cohortFilter) params.set("cohort_id", cohortFilter);
      const qs = params.toString();
      return apiWithAuth<{ data: SkillItem[]; meta: { total: number } }>(
        `/orgs/${orgId}/skills${qs ? `?${qs}` : ""}`,
      );
    },
  });

  const skills = data?.data ?? [];
  const cohorts = cohortsData?.data ?? [];

  return (
    <div className="space-y-6">
      {isError && <p className="mb-4 text-sm text-red-600">Failed to load skills. Please try again.</p>}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Skills</h1>
          <p className="mt-1 text-[hsl(var(--muted-foreground))]">
            Browse and practice skills in this organization.
          </p>
        </div>
        <Link href={`/dashboard/orgs/${orgId}/skills/new`}>
          <Button size="sm">New Skill</Button>
        </Link>
      </div>

      <div className="flex gap-3">
        <Input
          placeholder="Search skills..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <select
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
        {cohorts.length > 0 && (
          <select
            value={cohortFilter}
            onChange={(e) => setCohortFilter(e.target.value)}
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
          >
            <option value="">All cohorts</option>
            {cohorts.map((co) => (
              <option key={co.id} value={co.id}>
                {co.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {!isLoading && skills.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No skills found.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {skills.map((skill) => (
          <Link
            key={skill.id}
            href={`/dashboard/orgs/${orgId}/skills/${skill.id}`}
            className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
          >
            <div className="flex items-start justify-between">
              <h3 className="font-semibold group-hover:text-[hsl(var(--primary))]">
                {skill.name}
              </h3>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${DIFFICULTY_COLORS[skill.difficulty] ?? ""}`}
              >
                {skill.difficulty}
              </span>
            </div>
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
              {skill.description}
            </p>
            {(skill.tags ?? []).length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {(skill.tags ?? []).map((tag) => (
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

      {data?.meta && skills.length < data.meta.total && (
        <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
          Showing {skills.length} of {data.meta.total} skills
        </p>
      )}
    </div>
  );
}
