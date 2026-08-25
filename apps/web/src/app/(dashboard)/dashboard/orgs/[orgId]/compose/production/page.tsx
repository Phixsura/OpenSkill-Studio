"use client";

// Production solution composer (ADR-013 Part F): brief/profile →
// workflow chain + template + capability gaps → human confirm → Project.

import { Suspense, useState } from "react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Profile {
  id: string;
  context_type: string;
  status: string;
  structured_requirements: { goal?: string; output_type?: string };
}

interface Draft {
  id: string;
  status: string;
  materialized_entity_id: string | null;
  payload: {
    workflow_chain: { entity_id: string; name: string; order: number }[];
    template: { entity_id: string; name: string } | null;
    items: { entity_id: string; name: string; family: string }[];
    placeholders: { input_key: string; type: string; reason: string }[];
    gaps: { code: string; capability?: string; detail?: string }[];
    required_capabilities: { capability: string }[] | string[];
  };
}

function placeholderLabel(p: { input_key: string; type: string; reason: string }): string {
  if (p.reason === "no_producer")
    return `Input "${p.input_key}" (${p.type}): no workflow produces this — you will provide it`;
  if (p.reason === "needs_user_value")
    return `Input "${p.input_key}" (${p.type}): provided by you at run time`;
  return `Input "${p.input_key}" (${p.type}): ${p.reason}`;
}

function gapLabel(gap: { code: string; capability?: string; detail?: string }): string {
  if (gap.code === "NO_ELIGIBLE_PROVIDER")
    return `No provider connected for "${gap.capability}" — connect one in Providers`;
  if (gap.code === "NO_TEMPLATE_AVAILABLE")
    return "No matching project template found";
  if (gap.code === "NO_RELEASES") return gap.detail ?? "A workflow has no releases";
  return gap.detail ?? gap.code;
}

function ProductionComposerInner() {
  const { orgId } = useParams<{ orgId: string }>();
  const searchParams = useSearchParams();
  const profileParam = searchParams.get("profile");

  const [selectedProfile, setSelectedProfile] = useState<string>(profileParam ?? "");
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

  const composeMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Draft }>(`/orgs/${orgId}/drafts/production-solution`, {
        method: "POST",
        body: JSON.stringify({ profile_id: selectedProfile }),
      }),
    onSuccess: (res) => setDraft(res.data),
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Compose failed"),
  });

  const confirmMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { draft: Draft; materialized_entity_id: string } }>(
        `/orgs/${orgId}/drafts/${draft?.id}/confirm`,
        { method: "POST" },
      ),
    onSuccess: (res) => {
      setDraft(res.data.draft);
      toast.success("Project created");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Confirm failed"),
  });

  const confirmedDraft = draft?.status === "confirmed";
  const requiredCaps = (draft?.payload.required_capabilities ?? []).map((c) =>
    typeof c === "string" ? c : c.capability,
  );
  const gapCaps = new Set(
    (draft?.payload.gaps ?? [])
      .filter((g) => g.code === "NO_ELIGIBLE_PROVIDER" && g.capability)
      .map((g) => g.capability as string),
  );

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Compose Production Solution</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Assembles compatible workflow packs and a project template. You confirm before
          anything is created.
        </p>
      </div>

      <section className="space-y-2 rounded-lg border p-4">
        <h2 className="font-semibold">1. Requirement profile</h2>
        <select
          value={selectedProfile}
          onChange={(e) => {
            setSelectedProfile(e.target.value);
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
        <Button
          size="sm"
          onClick={() => composeMutation.mutate()}
          disabled={!selectedProfile || composeMutation.isPending}
        >
          {composeMutation.isPending ? "Composing..." : "Compose Solution"}
        </Button>
      </section>

      {draft && (
        <>
          <section className="space-y-3 rounded-lg border p-4">
            <h2 className="font-semibold">2. Workflow chain</h2>
            {draft.payload.workflow_chain.length === 0 ? (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                No matching workflows found.
              </p>
            ) : (
              <div className="flex flex-wrap items-center gap-2">
                {draft.payload.workflow_chain
                  .slice()
                  .sort((a, b) => a.order - b.order)
                  .map((wf, i) => (
                    <div key={wf.entity_id} className="flex items-center gap-2">
                      {i > 0 && (
                        <span
                          aria-hidden
                          className="text-[hsl(var(--muted-foreground))]"
                        >
                          →
                        </span>
                      )}
                      <div className="rounded-lg border px-4 py-3 text-sm font-medium">
                        {wf.name}
                      </div>
                    </div>
                  ))}
              </div>
            )}

            {draft.payload.template ? (
              <p className="text-sm">
                Project template:{" "}
                <span className="font-medium">{draft.payload.template.name}</span>
              </p>
            ) : (
              <p className="text-sm text-amber-700 dark:text-amber-400">
                No project template matched — the draft cannot be materialized without one.
              </p>
            )}
          </section>

          {(draft.payload.placeholders.length > 0 || draft.payload.gaps.length > 0) && (
            <section className="space-y-2 rounded-lg border p-4">
              <h2 className="font-semibold">3. Unresolved inputs & gaps</h2>
              {draft.payload.placeholders.map((p, i) => (
                <p key={i} className="text-sm text-[hsl(var(--muted-foreground))]">
                  ○ {placeholderLabel(p)}
                </p>
              ))}
              {draft.payload.gaps.map((g, i) => (
                <div
                  key={i}
                  className="rounded-md border border-amber-300 bg-amber-50 p-2.5 text-sm text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200"
                  role="alert"
                >
                  {gapLabel(g)}
                </div>
              ))}
            </section>
          )}

          {requiredCaps.length > 0 && (
            <section className="space-y-2 rounded-lg border p-4">
              <h2 className="font-semibold">Required capabilities</h2>
              <div className="flex flex-wrap gap-2">
                {requiredCaps.map((cap) => (
                  <span
                    key={cap}
                    className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      gapCaps.has(cap)
                        ? "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200"
                        : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                    }`}
                  >
                    {cap} {gapCaps.has(cap) ? "· no provider" : "· ready"}
                  </span>
                ))}
              </div>
            </section>
          )}

          {draft.payload.items.length > 0 && (
            <section className="space-y-2 rounded-lg border p-4">
              <h2 className="font-semibold">Recommended skill packs</h2>
              <ul className="list-inside list-disc text-sm">
                {draft.payload.items.map((item) => (
                  <li key={item.entity_id}>{item.name}</li>
                ))}
              </ul>
            </section>
          )}

          {!confirmedDraft && (
            <section className="space-y-3 rounded-lg border p-4">
              <h2 className="font-semibold">Confirm</h2>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                This will create a project from the template
                {draft.payload.template ? ` "${draft.payload.template.name}"` : ""} with{" "}
                {draft.payload.workflow_chain.length} workflow
                {draft.payload.workflow_chain.length === 1 ? "" : "s"} referenced.
              </p>
              <Button
                onClick={() => confirmMutation.mutate()}
                disabled={confirmMutation.isPending || !draft.payload.template}
              >
                {confirmMutation.isPending ? "Creating..." : "Confirm & Create Project"}
              </Button>
            </section>
          )}

          {confirmedDraft && draft.materialized_entity_id && (
            <div className="rounded-lg border border-green-300 bg-green-50 p-4 dark:border-green-700 dark:bg-green-950">
              <p className="text-sm font-medium text-green-800 dark:text-green-200">
                Project created.
              </p>
              <Link
                href={`/dashboard/orgs/${orgId}/projects/${draft.materialized_entity_id}`}
                className="mt-1 inline-block text-sm text-green-700 underline dark:text-green-300"
              >
                Open the project →
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function ProductionComposerPage() {
  return (
    <Suspense
      fallback={<p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
    >
      <ProductionComposerInner />
    </Suspense>
  );
}
