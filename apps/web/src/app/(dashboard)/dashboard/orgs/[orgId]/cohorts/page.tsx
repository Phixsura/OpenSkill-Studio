"use client";

import Link from "next/link";
import { toast } from "sonner";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

interface Cohort {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  status: string;
  starts_at: string | null;
  ends_at: string | null;
  max_learners: number | null;
  member_count: number;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  completed: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  archived: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
};

export default function CohortsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [maxLearners, setMaxLearners] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["cohorts", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Cohort[]; meta: { total: number } }>(
        `/orgs/${orgId}/cohorts`,
      ),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/cohorts`, {
        method: "POST",
        body: JSON.stringify({
          name,
          description: description || undefined,
          starts_at: startsAt || undefined,
          ends_at: endsAt || undefined,
          max_learners: maxLearners ? parseInt(maxLearners, 10) : undefined,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohorts", orgId] });
      setShowCreate(false);
      setName("");
      setDescription("");
      setStartsAt("");
      setEndsAt("");
      setMaxLearners("");
    },
    onError: (err: Error) => toast.error(err.message || "Failed to create cohort"),
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Cohorts</h1>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "+ New Cohort"}
        </Button>
      </div>

      {showCreate && (
        <div className="mb-6 rounded-lg border p-4">
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Cohort name (e.g. AI Visual Commerce — Fall 2026)"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
            />
            <textarea
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
              rows={2}
            />
            <div className="flex gap-3">
              <div className="flex-1">
                <label className="mb-1 block text-xs text-[hsl(var(--muted-foreground))]">
                  Start date
                </label>
                <input
                  type="datetime-local"
                  value={startsAt}
                  onChange={(e) => setStartsAt(e.target.value)}
                  className="w-full rounded border px-3 py-2 text-sm"
                />
              </div>
              <div className="flex-1">
                <label className="mb-1 block text-xs text-[hsl(var(--muted-foreground))]">
                  End date
                </label>
                <input
                  type="datetime-local"
                  value={endsAt}
                  onChange={(e) => setEndsAt(e.target.value)}
                  className="w-full rounded border px-3 py-2 text-sm"
                />
              </div>
              <div className="w-32">
                <label className="mb-1 block text-xs text-[hsl(var(--muted-foreground))]">
                  Max learners
                </label>
                <input
                  type="number"
                  value={maxLearners}
                  onChange={(e) => setMaxLearners(e.target.value)}
                  placeholder="∞"
                  min={1}
                  className="w-full rounded border px-3 py-2 text-sm"
                />
              </div>
            </div>
            <Button
              onClick={() => createMutation.mutate()}
              disabled={!name.trim() || createMutation.isPending}
            >
              Create Cohort
            </Button>
          </div>
        </div>
      )}

      {isError && (
        <p className="mb-4 text-sm text-red-600">Failed to load cohorts. Please try again.</p>
      )}

      {isLoading ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading cohorts...</p>
      ) : !isError && !data?.data.length ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No cohorts yet. Create one to start organizing your training programs.
        </p>
      ) : data?.data.length ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.data.map((cohort) => (
            <Link
              key={cohort.id}
              href={`/dashboard/orgs/${orgId}/cohorts/${cohort.id}`}
              className="rounded-lg border p-4 transition-shadow hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-semibold">{cohort.name}</h3>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs capitalize ${STATUS_COLORS[cohort.status] || ""}`}
                >
                  {cohort.status}
                </span>
              </div>
              {cohort.description && (
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
                  {cohort.description}
                </p>
              )}
              <div className="mt-3 flex gap-4 text-xs text-[hsl(var(--muted-foreground))]">
                <span>{cohort.member_count} member{cohort.member_count !== 1 ? "s" : ""}</span>
                {cohort.starts_at && (
                  <span>Starts {new Date(cohort.starts_at).toLocaleDateString()}</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
