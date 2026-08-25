"use client";

// Learning solution composer (ADR-013 Part E): recommend → draft → review →
// human confirm. Cuts, waivers, and gaps are always visible (R8).

import { Suspense, useState } from "react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { ExcludedSection, type ExcludedEntity } from "@/components/excluded-section";
import { MatchResultCard, type MatchResultItem } from "@/components/match-result-card";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Profile {
  id: string;
  context_type: string;
  status: string;
  structured_requirements: { goal?: string; time_budget?: number };
}

interface MatchRun {
  id: string;
  results: MatchResultItem[];
  excluded: ExcludedEntity[];
}

interface DraftItem {
  family: string;
  entity_id: string;
  name: string;
  order: number;
  required: boolean;
  status: string;
  reason_code?: string;
  evidence?: string;
  estimated_minutes?: number;
}

interface Draft {
  id: string;
  status: string;
  materialized_entity_id: string | null;
  payload: {
    items: DraftItem[];
    gaps: { code: string; capability?: string; minimum_minutes?: number }[];
    estimated_total_minutes?: number;
  };
}

const ITEM_STATUS_STYLES: Record<string, { label: string; className: string }> = {
  included: { label: "", className: "" },
  waived: {
    label: "Already completed",
    className: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  },
  cut_for_budget: {
    label: "Cut for budget",
    className: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  },
  removed_by_user: {
    label: "Removed",
    className: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  },
};

function gapLabel(gap: { code: string; capability?: string; minimum_minutes?: number }): string {
  if (gap.code === "NO_CONTENT_AVAILABLE")
    return `No content available for "${gap.capability}"`;
  if (gap.code === "BUDGET_INFEASIBLE")
    return `Time budget too small — required items need at least ${gap.minimum_minutes} minutes`;
  return gap.code;
}

function LearningComposerInner() {
  const { orgId } = useParams<{ orgId: string }>();
  const searchParams = useSearchParams();
  const profileParam = searchParams.get("profile");

  const [selectedProfile, setSelectedProfile] = useState<string>(profileParam ?? "");
  const [matchRun, setMatchRun] = useState<MatchRun | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);

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
  const profile = confirmedProfiles.find((p) => p.id === selectedProfile);

  const matchMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: MatchRun }>(`/orgs/${orgId}/match`, {
        method: "POST",
        body: JSON.stringify({
          requirement_profile_id: selectedProfile,
          target_entity_type: "skill_pack",
          limit: 20,
        }),
      }),
    onSuccess: (res) => setMatchRun(res.data),
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Matching failed"),
  });

  const composeMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Draft }>(`/orgs/${orgId}/drafts/learning-path`, {
        method: "POST",
        body: JSON.stringify({ profile_id: selectedProfile }),
      }),
    onSuccess: (res) => setDraft(res.data),
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Compose failed"),
  });

  const removeMutation = useMutation({
    mutationFn: (entityId: string) =>
      apiWithAuth<{ data: Draft }>(`/orgs/${orgId}/drafts/${draft?.id}`, {
        method: "PATCH",
        body: JSON.stringify({ remove_entity_ids: [entityId] }),
      }),
    onSuccess: (res) => setDraft(res.data),
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Remove failed"),
  });

  const confirmMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { draft: Draft; materialized_entity_id: string } }>(
        `/orgs/${orgId}/drafts/${draft?.id}/confirm`,
        { method: "POST" },
      ),
    onSuccess: (res) => {
      setDraft(res.data.draft);
      toast.success("Learning path created");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Confirm failed"),
  });

  const activeItems =
    draft?.payload.items.filter((i) => i.status === "included") ?? [];
  const confirmedDraft = draft?.status === "confirmed";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Compose Learning Path</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Recommendations and drafts are proposals — nothing is created until you confirm.
        </p>
      </div>

      {/* Step 1: profile */}
      <section className="space-y-2 rounded-lg border p-4">
        <h2 className="font-semibold">1. Requirement profile</h2>
        <select
          value={selectedProfile}
          onChange={(e) => {
            setSelectedProfile(e.target.value);
            setMatchRun(null);
            setDraft(null);
          }}
          className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
          aria-label="Select confirmed profile"
        >
          <option value="">Select a confirmed profile…</option>
          {confirmedProfiles.map((p) => (
            <option key={p.id} value={p.id}>
              {p.structured_requirements.goal ?? p.id} ({p.context_type})
            </option>
          ))}
        </select>
        {profile && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Goal: {profile.structured_requirements.goal ?? "—"}
            {profile.structured_requirements.time_budget
              ? ` · Budget: ${profile.structured_requirements.time_budget} min`
              : ""}
          </p>
        )}
      </section>

      {/* Step 2: recommendations */}
      <section className="space-y-3 rounded-lg border p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">2. Recommendations</h2>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => matchMutation.mutate()}
            disabled={!selectedProfile || matchMutation.isPending}
          >
            {matchMutation.isPending ? "Matching..." : "Get Recommendations"}
          </Button>
        </div>
        {matchRun && (
          <>
            <div className="space-y-3">
              {matchRun.results.map((r) => (
                <MatchResultCard key={r.entity_id} result={r} />
              ))}
              {matchRun.results.length === 0 && (
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  No eligible skill packs matched.
                </p>
              )}
            </div>
            <ExcludedSection excluded={matchRun.excluded} />
          </>
        )}
      </section>

      {/* Step 3: draft */}
      <section className="space-y-3 rounded-lg border p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">3. Draft path</h2>
          <Button
            size="sm"
            onClick={() => composeMutation.mutate()}
            disabled={!selectedProfile || composeMutation.isPending || confirmedDraft}
          >
            {composeMutation.isPending ? "Composing..." : "Compose Draft"}
          </Button>
        </div>

        {draft && (
          <>
            {draft.payload.gaps.map((gap, i) => (
              <div
                key={i}
                className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200"
                role="alert"
              >
                {gapLabel(gap)}
              </div>
            ))}

            <ol className="space-y-2">
              {draft.payload.items
                .slice()
                .sort((a, b) => a.order - b.order)
                .map((item) => {
                  const style = ITEM_STATUS_STYLES[item.status];
                  return (
                    <li
                      key={item.entity_id}
                      className={`flex items-center gap-3 rounded-md border p-3 ${
                        item.status === "cut_for_budget" ? "opacity-60" : ""
                      }`}
                    >
                      <span className="text-sm text-[hsl(var(--muted-foreground))]">
                        {item.order + 1}.
                      </span>
                      <span
                        className={
                          item.status === "cut_for_budget" ? "line-through" : ""
                        }
                      >
                        {item.name}
                      </span>
                      {item.estimated_minutes != null && (
                        <span className="text-xs text-[hsl(var(--muted-foreground))]">
                          {item.estimated_minutes} min
                        </span>
                      )}
                      {style?.label && (
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${style.className}`}
                          title={item.evidence}
                        >
                          {style.label}
                        </span>
                      )}
                      {!confirmedDraft && item.status === "included" && (
                        <button
                          onClick={() => removeMutation.mutate(item.entity_id)}
                          className="ml-auto text-xs text-red-600 hover:underline"
                        >
                          Remove
                        </button>
                      )}
                    </li>
                  );
                })}
            </ol>
            {draft.payload.estimated_total_minutes != null && (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Estimated total: {draft.payload.estimated_total_minutes} minutes
              </p>
            )}
          </>
        )}
      </section>

      {/* Step 4: confirm */}
      {draft && !confirmedDraft && (
        <section className="space-y-3 rounded-lg border p-4">
          <h2 className="font-semibold">4. Confirm</h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            This will create a draft learning path with {activeItems.length} item
            {activeItems.length === 1 ? "" : "s"}. You can edit it before publishing.
          </p>
          <Button
            onClick={() => confirmMutation.mutate()}
            disabled={confirmMutation.isPending || activeItems.length === 0}
          >
            {confirmMutation.isPending ? "Creating..." : "Confirm & Create Path"}
          </Button>
        </section>
      )}

      {confirmedDraft && draft?.materialized_entity_id && (
        <div className="rounded-lg border border-green-300 bg-green-50 p-4 dark:border-green-700 dark:bg-green-950">
          <p className="text-sm font-medium text-green-800 dark:text-green-200">
            Learning path created.
          </p>
          <Link
            href={`/dashboard/orgs/${orgId}/paths/${draft.materialized_entity_id}`}
            className="mt-1 inline-block text-sm text-green-700 underline dark:text-green-300"
          >
            Open the path →
          </Link>
        </div>
      )}
    </div>
  );
}

export default function LearningComposerPage() {
  return (
    <Suspense
      fallback={<p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
    >
      <LearningComposerInner />
    </Suspense>
  );
}
