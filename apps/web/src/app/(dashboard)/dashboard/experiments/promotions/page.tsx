"use client";
/** Promotion rollout monitor (ADR-017 Part K): draft → approve → apply,
 * idempotent apply, target-domain draft refs. Status filter is URL state. */

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { EmptyState, ErrorBanner, ExperimentsNav, Pill, SectionCard } from "../components";
import { PROMOTION_STATUSES, STATUS_STYLES, fmtDate, type PromotionDraft } from "../lib";

/** Poll every 5s while an async apply is in flight; otherwise rest. */
export function promotionsRefetchInterval(
  drafts: { status: string }[] | undefined,
): number | false {
  return drafts?.some((d) => d.status === "applying") ? 5000 : false;
}

export default function PromotionsPage() {
  return (
    <Suspense>
      <PromotionsInner />
    </Suspense>
  );
}

function PromotionsInner() {
  const router = useRouter();
  const params = useSearchParams();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [status, setStatusState] = useState(params.get("status") ?? "");
  const setStatus = (v: string) => {
    setStatusState(v);
    router.replace(`/dashboard/experiments/promotions${v ? `?status=${v}` : ""}`, {
      scroll: false,
    });
  };

  const { data, isLoading } = useQuery({
    queryKey: ["experiment-promotion-drafts", status],
    // round 111: an in-flight async apply resolves out-of-band — poll while
    // any draft is 'applying' so the operator sees it land without refreshing
    refetchInterval: (query) => promotionsRefetchInterval(query.state.data?.data),
    queryFn: () =>
      apiWithAuth<{ data: PromotionDraft[] }>(
        `/experiments/promotion-drafts?limit=100${status ? `&status=${status}` : ""}`,
      ),
  });

  const act = useMutation({
    mutationFn: ({
      id,
      action,
    }: {
      id: string;
      action: "approve" | "reject" | "apply" | "apply?background=true";
    }) =>
      apiWithAuth(`/experiments/promotion-drafts/${id}/${action}`, { method: "POST", body: "{}" }),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["experiment-promotion-drafts"] });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Action failed"),
  });

  const drafts = data?.data ?? [];

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">Promotion drafts</h1>
      <ErrorBanner message={error} />
      <label className="text-sm text-slate-600">
        Status{" "}
        <select
          aria-label="Status filter"
          className="rounded-md border px-2 py-1 text-sm"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">all</option>
          {PROMOTION_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <SectionCard title="Drafts (apply creates the target domain's own draft object — never a production mutation)">
        {isLoading ? (
          <div className="text-sm text-slate-500">Loading…</div>
        ) : drafts.length === 0 ? (
          <EmptyState message="No promotion drafts." />
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="py-1 pr-3">Target</th>
                <th className="py-1 pr-3">Ref</th>
                <th className="py-1 pr-3">Status</th>
                <th className="py-1 pr-3">Applied ref</th>
                <th className="py-1 pr-3">Created</th>
                <th className="py-1 pr-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {drafts.map((d) => (
                <tr key={d.id} className="border-t">
                  <td className="py-1 pr-3 font-medium">{d.target_type}</td>
                  <td className="py-1 pr-3 text-xs">{d.target_ref}</td>
                  <td className="py-1 pr-3">
                    <Pill value={d.status} styles={STATUS_STYLES} />
                  </td>
                  <td className="py-1 pr-3 text-xs">
                    {d.applied_ref ?? "—"}
                    {d.apply_error ? <div className="text-rose-700">{d.apply_error}</div> : null}
                  </td>
                  <td className="py-1 pr-3 text-xs text-slate-500">{fmtDate(d.created_at)}</td>
                  <td className="py-1 pr-3">
                    <div className="flex gap-1">
                      {d.status === "draft" ? (
                        <>
                          <button
                            type="button"
                            className="rounded border px-2 py-0.5 text-xs"
                            onClick={() => act.mutate({ id: d.id, action: "approve" })}
                          >
                            Approve
                          </button>
                          <button
                            type="button"
                            className="rounded border px-2 py-0.5 text-xs text-rose-700"
                            onClick={() => act.mutate({ id: d.id, action: "reject" })}
                          >
                            Reject
                          </button>
                        </>
                      ) : null}
                      {d.status === "approved" ? (
                        <>
                          <button
                            type="button"
                            className="rounded border px-2 py-0.5 text-xs"
                            onClick={() => act.mutate({ id: d.id, action: "apply" })}
                          >
                            Apply
                          </button>
                          <button
                            type="button"
                            className="rounded border px-2 py-0.5 text-xs"
                            title="Queue through the worker; failures land in apply_error and are retryable"
                            onClick={() =>
                              act.mutate({ id: d.id, action: "apply?background=true" })
                            }
                          >
                            Apply async
                          </button>
                        </>
                      ) : null}
                      {d.status === "applying" ? (
                        <span className="text-xs text-slate-500">queued…</span>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </SectionCard>
    </div>
  );
}
