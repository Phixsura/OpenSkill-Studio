"use client";
/** Decision detail + promotion draft creation (ADR-017 Parts J/K). Drafts
 * target whitelisted domains only — no employment action exists. */

import Link from "next/link";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { ErrorBanner, ExperimentsNav, JsonPacketButton, Pill, SectionCard } from "../../components";
import {
  PROMOTION_TARGET_TYPES,
  STATUS_STYLES,
  fmtDate,
  type DecisionRecord,
  type PromotionDraft,
} from "../../lib";

export default function DecisionDetailPage() {
  const { decisionId } = useParams<{ decisionId: string }>();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [draftForm, setDraftForm] = useState({
    target_type: "matching_config",
    target_ref: "",
    draft_payload: "{}",
  });

  const { data } = useQuery({
    queryKey: ["experiment-decision", decisionId],
    queryFn: () => apiWithAuth<{ data: DecisionRecord }>(`/experiments/decisions/${decisionId}`),
  });
  const record = data?.data;

  // round 234: the cited look's WARNINGS belong next to the evidence —
  // the decision-maker sees the caveats without leaving the page
  const { data: historyData } = useQuery({
    queryKey: ["experiment-analysis-history", record?.experiment_id],
    enabled: Boolean(record?.experiment_id),
    queryFn: () =>
      apiWithAuth<{ data: { result_hash?: string; warnings?: string[] }[] }>(
        `/experiments/${record?.experiment_id}/analysis/history?limit=200`,
      ),
  });
  const citedLook = (historyData?.data ?? []).find(
    (look) => look.result_hash === record?.analysis_result_hash,
  );
  // round 239: the record FREEZES its warnings at decide time — prefer the
  // frozen copy; history is the fallback for pre-239 records only
  const frozen = record?.evidence?.cited_warnings;
  const citedWarnings = frozen ?? citedLook?.warnings ?? [];

  const createDraft = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: PromotionDraft }>(
        `/experiments/decisions/${decisionId}/promotion-drafts`,
        {
          method: "POST",
          body: JSON.stringify({
            target_type: draftForm.target_type,
            target_ref: draftForm.target_ref,
            draft_payload: JSON.parse(draftForm.draft_payload || "{}"),
          }),
        },
      ),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["experiment-promotion-drafts"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Failed to create draft"),
  });

  if (!record) return <div className="p-6 text-sm text-slate-500">Loading…</div>;

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-xl font-semibold">Decision</h1>
        <Pill
          value={record.decision}
          styles={{
            promote: "bg-green-100 text-green-800",
            reject: "bg-rose-100 text-rose-800",
            inconclusive: "bg-slate-100 text-slate-700",
            extend: "bg-sky-100 text-sky-800",
          }}
        />
        <span className="text-xs text-slate-500">{fmtDate(record.created_at)}</span>
      </div>
      <ErrorBanner message={error} />
      <SectionCard title="Record (immutable)">
        <p className="text-sm">{record.summary}</p>
        <dl className="mt-3 grid gap-3 text-sm md:grid-cols-3">
          <div>
            <dt className="text-xs text-slate-500">Experiment</dt>
            <dd>
              <Link
                href={`/dashboard/experiments/${record.experiment_id}`}
                className="text-slate-900 hover:underline"
              >
                {record.experiment_id}
              </Link>
            </dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Domain</dt>
            <dd>{record.domain}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Analysis type</dt>
            <dd>{record.analysis_type}</dd>
          </div>
          <div className="md:col-span-3">
            <dt className="text-xs text-slate-500">Analysis result hash (evidence link)</dt>
            <dd>
              <code className="text-xs">{record.analysis_result_hash}</code>
              <div className="mt-1">
                <JsonPacketButton
                  data={{ decision: record, cited_look_warnings: citedWarnings }}
                  filename={`decision-${record.id}.json`}
                />
              </div>
              {citedWarnings.length > 0 ? (
                <div className="mt-1 flex flex-wrap gap-1">
                  {citedWarnings.map((w) => (
                    <span
                      key={w}
                      className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] text-amber-800"
                    >
                      {w}
                    </span>
                  ))}
                </div>
              ) : null}
            </dd>
          </div>
        </dl>
      </SectionCard>

      {record.decision === "promote" && record.analysis_type === "randomized" ? (
        <SectionCard title="Create promotion draft (target-domain DRAFT object)">
          <div className="grid gap-3 md:grid-cols-3">
            <label className="text-xs text-slate-600">
              Target type
              <select
                className="block w-full rounded-md border px-2 py-1.5 text-sm"
                value={draftForm.target_type}
                onChange={(e) => setDraftForm({ ...draftForm, target_type: e.target.value })}
              >
                {PROMOTION_TARGET_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-xs text-slate-600">
              Target ref
              <input
                className="block w-full rounded-md border px-2 py-1.5 text-sm"
                value={draftForm.target_ref}
                onChange={(e) => setDraftForm({ ...draftForm, target_ref: e.target.value })}
              />
            </label>
            <label className="text-xs text-slate-600">
              Draft payload (JSON)
              <input
                className="block w-full rounded-md border px-2 py-1.5 text-sm"
                value={draftForm.draft_payload}
                onChange={(e) => setDraftForm({ ...draftForm, draft_payload: e.target.value })}
              />
            </label>
          </div>
          <button
            type="button"
            onClick={() => createDraft.mutate()}
            className="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white"
          >
            Create draft
          </button>
          {createDraft.isSuccess ? (
            <p className="mt-2 text-sm text-emerald-700">
              Draft created — review it on the{" "}
              <Link href="/dashboard/experiments/promotions" className="underline">
                Promotions
              </Link>{" "}
              board.
            </p>
          ) : null}
        </SectionCard>
      ) : (
        <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
          Promotion drafts require a <Pill value="promote" styles={STATUS_STYLES} /> decision on a
          randomized analysis.
        </div>
      )}
    </div>
  );
}
