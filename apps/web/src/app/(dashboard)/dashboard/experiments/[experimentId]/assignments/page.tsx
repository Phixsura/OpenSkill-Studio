"use client";
/** Assignment diagnostics + SRM banner + dry-run preview (ADR-017 Part L). */

import Link from "next/link";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { ErrorBanner, ExperimentsNav, SectionCard, CsvExportButton } from "../../components";
import { UNIT_TYPES, type GuardrailEvent } from "../../lib";

interface AssignmentStats {
  variants: Record<string, number>;
  holdout: number;
  total: number;
}

interface ExposureFunnel {
  funnel: Record<string, { assigned: number; exposed_units: number }>;
  holdout: number;
  last_exposure_at: string | null;
}

export default function AssignmentsPage() {
  const { experimentId } = useParams<{ experimentId: string }>();
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState({ unit_type: "user", unit_id: "" });
  const [previewResult, setPreviewResult] = useState<Record<string, unknown> | null>(null);

  const stats = useQuery({
    queryKey: ["experiment-assignments", experimentId],
    queryFn: () =>
      apiWithAuth<{ data: AssignmentStats }>(`/experiments/${experimentId}/assignments`),
  });
  const funnel = useQuery({
    queryKey: ["experiment-exposures", experimentId],
    queryFn: () =>
      apiWithAuth<{ data: ExposureFunnel }>(`/experiments/${experimentId}/exposures/stats`),
  });
  const guardrails = useQuery({
    queryKey: ["experiment-guardrail-events", experimentId],
    queryFn: () =>
      apiWithAuth<{ data: GuardrailEvent[] }>(
        `/experiments/${experimentId}/guardrails/events?limit=50`,
      ),
  });
  // Defect #93: the banner must cover the whole SRM family, not just the
  // cumulative key — windowed and exposure variants are the same alarm class
  const SRM_FAMILY: Record<string, string> = {
    __srm__: "assignment counts diverge from spec weights (χ² alert)",
    __srm_window__:
      "the last-24h assignment slice diverges from spec weights — a LATE randomization break",
    __exposure_srm__: "exposed units diverge from assignment proportions — trigger bias (χ² alert)",
    __exposure_srm_window__:
      "the last-24h exposure slice diverges from assignment proportions — a LATE trigger-bias regression",
  };
  const srmAlert = (guardrails.data?.data ?? []).find((e) => e.guardrail_key in SRM_FAMILY);

  const runPreview = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Record<string, unknown> }>(
        `/experiments/${experimentId}/assignments:preview`,
        { method: "POST", body: JSON.stringify(preview) },
      ),
    onSuccess: (res) => {
      setError(null);
      setPreviewResult(res.data);
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Preview failed"),
  });

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">
        <Link href={`/dashboard/experiments/${experimentId}`} className="hover:underline">
          Experiment
        </Link>{" "}
        · Assignments
      </h1>
      <CsvExportButton
        path={`/experiments/${experimentId}/assignments/export`}
        filename={`experiment-${experimentId}-assignments.csv`}
      />
      <ErrorBanner message={error} />
      {srmAlert ? (
        <div
          role="alert"
          className="rounded-md border border-rose-300 bg-rose-50 p-3 text-sm text-rose-900"
        >
          <strong>Sample-ratio mismatch detected</strong> — {SRM_FAMILY[srmAlert.guardrail_key]}.
          Treat results as suspect until the enrollment path is diagnosed.
        </div>
      ) : null}
      <SectionCard title="Assignments by variant (ITT)">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="py-1">Variant</th>
              <th className="py-1">Assigned</th>
              <th className="py-1">Exposed units</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(stats.data?.data.variants ?? {}).map(([variant, count]) => (
              <tr key={variant} className="border-t">
                <td className="py-1 font-medium">{variant}</td>
                <td className="py-1">{count}</td>
                <td className="py-1">{funnel.data?.data.funnel[variant]?.exposed_units ?? 0}</td>
              </tr>
            ))}
            <tr className="border-t text-slate-500">
              <td className="py-1">holdout</td>
              <td className="py-1">{stats.data?.data.holdout ?? 0}</td>
              <td className="py-1">—</td>
            </tr>
          </tbody>
        </table>
        <p className="mt-2 text-xs text-slate-500">
          Last exposure:{" "}
          {funnel.data?.data.last_exposure_at
            ? new Date(funnel.data.data.last_exposure_at).toLocaleString()
            : "none recorded"}
        </p>
      </SectionCard>

      <SectionCard title="Preview bucketing (dry-run, no writes)">
        <div className="flex flex-wrap items-end gap-2">
          <label className="text-xs text-slate-600">
            Unit type
            <select
              className="block rounded-md border px-2 py-1 text-sm"
              value={preview.unit_type}
              onChange={(e) => setPreview({ ...preview, unit_type: e.target.value })}
            >
              {UNIT_TYPES.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs text-slate-600">
            Unit id
            <input
              className="block rounded-md border px-2 py-1 text-sm"
              value={preview.unit_id}
              onChange={(e) => setPreview({ ...preview, unit_id: e.target.value })}
            />
          </label>
          <button
            type="button"
            onClick={() => runPreview.mutate()}
            className="rounded-md border px-3 py-1.5 text-sm"
          >
            Preview
          </button>
        </div>
        {previewResult ? (
          <pre className="mt-3 overflow-x-auto rounded bg-slate-50 p-2 text-xs">
            {JSON.stringify(previewResult, null, 2)}
          </pre>
        ) : null}
      </SectionCard>
    </div>
  );
}
