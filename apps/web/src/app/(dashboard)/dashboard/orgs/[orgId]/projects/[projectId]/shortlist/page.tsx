"use client";

// Creator shortlist (ADR-013 Part G): evidence-first cards, transparent gaps,
// human assignment only — the system never auto-assigns (R9).

import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Profile {
  id: string;
  context_type: string;
  status: string;
  structured_requirements: { goal?: string };
}

interface EvidenceRow {
  evidence_type: string;
  score: number | null;
  occurred_at: string;
}

interface ShortlistCreator {
  entity_id: string;
  name: string | null;
  rank: number | null;
  score: number | null;
  tier: string | null;
  reasons: { code: string; label: string }[];
  gaps: { code: string; label: string }[];
  evidence: Record<string, EvidenceRow[]>;
}

interface Shortlist {
  match_run_id: string;
  results: ShortlistCreator[];
  excluded: { entity_id: string; name?: string; failures: { detail?: string; code: string }[] }[];
}

interface Assignment {
  id: string;
  user_id: string;
  status: string;
  created_at: string;
}

const TIER_STYLES: Record<string, string> = {
  great: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  good: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  fair: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
};

const ASSIGN_STATUS_STYLES: Record<string, string> = {
  offered: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  accepted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  declined: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function CreatorShortlistPage() {
  const { orgId, projectId } = useParams<{ orgId: string; projectId: string }>();
  const queryClient = useQueryClient();
  const [profileId, setProfileId] = useState("");
  const [shortlist, setShortlist] = useState<Shortlist | null>(null);
  // Two-click assign confirmation (no window.confirm)
  const [armedUserId, setArmedUserId] = useState<string | null>(null);

  const { data: profilesData } = useQuery({
    queryKey: ["requirement-profiles", orgId, "all"],
    queryFn: async () => {
      // per_page=100 is the API cap — follow has_more so orgs with more
      // than 100 profiles still see every confirmed one in the select.
      const all: Profile[] = [];
      let page = 1;
      let hasMore = true;
      while (hasMore && page <= 10) {
        const res = await apiWithAuth<{ data: Profile[]; meta: { has_more: boolean } }>(
          `/orgs/${orgId}/requirement-profiles?page=${page}&per_page=100`,
        );
        all.push(...res.data);
        hasMore = res.meta?.has_more ?? false;
        page += 1;
      }
      return { data: all };
    },
  });
  const confirmedProfiles = (profilesData?.data ?? []).filter(
    (p) => p.status === "confirmed",
  );

  const { data: assignmentsData } = useQuery({
    queryKey: ["creator-assignments", orgId, projectId],
    queryFn: () =>
      apiWithAuth<{ data: Assignment[] }>(
        `/orgs/${orgId}/creator-assignments?project_id=${projectId}`,
      ),
  });
  const assignments = assignmentsData?.data ?? [];

  const shortlistMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Shortlist }>(
        `/orgs/${orgId}/projects/${projectId}/creator-shortlist?profile_id=${profileId}`,
      ),
    onSuccess: (res) => setShortlist(res.data),
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Shortlist failed"),
  });

  const assignMutation = useMutation({
    mutationFn: (userId: string) =>
      apiWithAuth(`/orgs/${orgId}/creator-assignments`, {
        method: "POST",
        body: JSON.stringify({
          project_id: projectId,
          user_id: userId,
          match_run_id: shortlist?.match_run_id ?? null,
        }),
      }),
    onSuccess: () => {
      toast.success("Assignment offered — the creator can accept or decline");
      setArmedUserId(null);
      queryClient.invalidateQueries({
        queryKey: ["creator-assignments", orgId, projectId],
      });
    },
    onError: (err) => {
      setArmedUserId(null);
      toast.error(err instanceof ApiError ? err.message : "Assignment failed");
    },
  });

  const assignedUserIds = new Set(assignments.map((a) => a.user_id));

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Creator Shortlist</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Ranked by verified platform evidence. Assignment is always your decision —
          creators accept or decline the offer.
        </p>
      </div>

      <section className="space-y-2 rounded-lg border p-4">
        <label htmlFor="profile" className="text-sm font-medium">
          Requirement profile
        </label>
        <select
          id="profile"
          value={profileId}
          onChange={(e) => setProfileId(e.target.value)}
          className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="">Select a confirmed profile…</option>
          {confirmedProfiles.map((p) => (
            <option key={p.id} value={p.id}>
              {p.structured_requirements.goal ?? p.id} ({p.context_type})
            </option>
          ))}
        </select>
        <Button
          size="sm"
          onClick={() => shortlistMutation.mutate()}
          disabled={!profileId || shortlistMutation.isPending}
        >
          {shortlistMutation.isPending ? "Building shortlist..." : "Build Shortlist"}
        </Button>
      </section>

      {shortlist && (
        <section className="space-y-3">
          {shortlist.results.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              No eligible creators matched the requirements.
            </p>
          )}
          {shortlist.results.map((creator) => (
            <div key={creator.entity_id} className="rounded-lg border p-4">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  {creator.rank != null && (
                    <span className="text-sm text-[hsl(var(--muted-foreground))]">
                      #{creator.rank}
                    </span>
                  )}
                  <span className="font-semibold">{creator.name ?? creator.entity_id}</span>
                  {creator.tier && (
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${TIER_STYLES[creator.tier] ?? ""}`}
                      title={
                        creator.score != null
                          ? `Score: ${creator.score.toFixed(4)}`
                          : undefined
                      }
                    >
                      {creator.tier === "great"
                        ? "Excellent match"
                        : creator.tier === "good"
                          ? "Good match"
                          : "Fair match"}
                    </span>
                  )}
                </div>
                {assignedUserIds.has(creator.entity_id) ? (
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    Already offered
                  </span>
                ) : armedUserId === creator.entity_id ? (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => assignMutation.mutate(creator.entity_id)}
                      disabled={assignMutation.isPending}
                    >
                      Confirm offer?
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setArmedUserId(null)}
                    >
                      Cancel
                    </Button>
                  </div>
                ) : (
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => setArmedUserId(creator.entity_id)}
                  >
                    Assign
                  </Button>
                )}
              </div>

              {creator.reasons.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {creator.reasons.slice(0, 3).map((r) => (
                    <span
                      key={r.code + r.label}
                      className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs"
                    >
                      {r.label}
                    </span>
                  ))}
                </div>
              )}

              {creator.gaps.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {creator.gaps.map((gap) => (
                    <li
                      key={gap.code + gap.label}
                      className="text-xs text-amber-700 dark:text-amber-400"
                    >
                      ⚠ {gap.label} — consider a skill pack to close this gap
                    </li>
                  ))}
                </ul>
              )}

              {Object.keys(creator.evidence).length > 0 && (
                <details className="mt-3">
                  <summary className="cursor-pointer text-xs font-medium text-[hsl(var(--muted-foreground))]">
                    Verified evidence
                  </summary>
                  <div className="mt-2 space-y-2">
                    {Object.entries(creator.evidence).map(([capability, rows]) => (
                      <div key={capability}>
                        <p className="text-xs font-medium">{capability}</p>
                        <ul className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                          {rows.map((row, i) => (
                            <li key={i}>
                              {row.evidence_type.replace(/_/g, " ")}
                              {row.score != null ? ` · score ${row.score}` : ""} ·{" "}
                              {new Date(row.occurred_at).toLocaleDateString()}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          ))}

          {shortlist.excluded.length > 0 && (
            <details className="rounded-lg border border-dashed p-4">
              <summary className="cursor-pointer text-sm font-medium text-[hsl(var(--muted-foreground))]">
                Not eligible ({shortlist.excluded.length})
              </summary>
              <ul className="mt-2 space-y-1 text-sm">
                {shortlist.excluded.map((e) => (
                  <li key={e.entity_id}>
                    <span className="font-medium">{e.name ?? e.entity_id}</span>
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      {" "}
                      — {e.failures.map((f) => f.detail ?? f.code).join("; ")}
                    </span>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </section>
      )}

      {assignments.length > 0 && (
        <section className="space-y-2 rounded-lg border p-4">
          <h2 className="font-semibold">Assignments</h2>
          <ul className="space-y-1.5">
            {assignments.map((a) => (
              <li key={a.id} className="flex items-center gap-2 text-sm">
                <span className="font-mono text-xs">{a.user_id}</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${ASSIGN_STATUS_STYLES[a.status] ?? ""}`}
                >
                  {a.status}
                </span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(a.created_at).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
