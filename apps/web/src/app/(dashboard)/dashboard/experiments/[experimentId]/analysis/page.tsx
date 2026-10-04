"use client";
/** Analysis view (ADR-017 Part L §10): CIs lead, p-values support.
 * Observational analyses render a prominent no-causal-claim banner; the
 * result hash is surfaced because decisions must reference it. */

import Link from "next/link";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { ErrorBanner, ExperimentsNav, SectionCard } from "../../components";
import { fmtNum } from "../../lib";

interface Comparison {
  effect?: number;
  relative?: number | null;
  ci?: [number, number];
  p?: number;
  always_valid_p?: number;
  boundary_z?: number;
  significant_at_boundary?: boolean;
  p_beat_control?: number;
  expected_loss?: number;
  credible_interval?: [number, number];
  passes_fdr?: boolean;
  insufficient_data?: boolean;
  caveat?: string;
  quantiles?: Record<
    string,
    { control: number; treatment: number; diff: number; ci: [number, number] }
  >;
  cuped?: {
    effect: number;
    ci: [number, number];
    // single-covariate shape carries variance_reduction_pct; the §4.6 v3
    // multi shape (mode === "multi") carries theta per covariate instead
    variance_reduction_pct?: number;
    mode?: string;
    covariates?: string[];
    caveat?: string;
  };
  corpus_prior?: { n_experiments: number; mean: number; sd: number };
  shrunk_effect?: number;
  time_stratified?: { effect: number; se: number; ci: [number, number]; strata: number };
}

interface AnalysisResult {
  engine: string;
  sequential: string;
  analysis_type: string;
  causal_claim: boolean;
  caveat?: string;
  control: string;
  looks?: { used: number; max: number };
  bandit?: {
    metric: string;
    p_best: Record<string, number>;
    suggested_weights_bp: Record<string, number>;
  };
  warnings: string[];
  power?: {
    metric_key: string;
    baseline_rate: number;
    mde: number;
    required_n_per_arm: number;
    min_arm_n: number;
    powered: boolean;
  };
  result_hash: string;
  metrics: Record<
    string,
    {
      role: string;
      kind?: string;
      comparisons?: Record<string, Comparison>;
      insufficient_data?: boolean;
    }
  >;
}

function CiBar({ ci, effect }: { ci: [number, number]; effect: number }) {
  const [lo, hi] = ci;
  const span = Math.max(Math.abs(lo), Math.abs(hi), 1e-9) * 2.2;
  const pct = (v: number) => `${((v + span / 2) / span) * 100}%`;
  return (
    <div className="relative h-4 w-48 rounded bg-slate-100" aria-label="confidence interval">
      <div className="absolute inset-y-0 w-px bg-slate-400" style={{ left: pct(0) }} />
      <div
        className={`absolute inset-y-1 rounded ${lo > 0 || hi < 0 ? "bg-emerald-400" : "bg-slate-300"}`}
        style={{
          left: pct(Math.min(lo, hi)),
          width: `calc(${pct(Math.max(lo, hi))} - ${pct(Math.min(lo, hi))})`,
        }}
      />
      <div className="absolute inset-y-0 w-0.5 bg-slate-900" style={{ left: pct(effect) }} />
    </div>
  );
}

export default function AnalysisPage() {
  const { experimentId } = useParams<{ experimentId: string }>();
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [segment, setSegment] = useState("");

  const segments = useQuery({
    queryKey: ["experiment-segments", experimentId],
    queryFn: () => apiWithAuth<{ data: string[] }>(`/experiments/${experimentId}/segments`),
  });

  interface LookEntry {
    at: string | null;
    sequential: string | null;
    look: number | null;
    result_hash: string | null;
    automated: boolean;
  }
  const history = useQuery({
    queryKey: ["experiment-analysis-history", experimentId],
    queryFn: () =>
      apiWithAuth<{ data: LookEntry[] }>(`/experiments/${experimentId}/analysis/history`),
  });

  const run = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: AnalysisResult }>(
        `/experiments/${experimentId}/analysis${segment ? `?segment=${encodeURIComponent(segment)}` : ""}`,
        {
          method: "POST",
          body: "{}",
        },
      ),
    onSuccess: (res) => {
      setError(null);
      setResult(res.data);
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Analysis failed"),
  });

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">
          <Link href={`/dashboard/experiments/${experimentId}`} className="hover:underline">
            Experiment
          </Link>{" "}
          · Analysis
        </h1>
        <div className="flex items-center gap-2">
          {(segments.data?.data ?? []).length > 0 ? (
            <select
              aria-label="Segment"
              className="rounded-md border px-2 py-1.5 text-sm"
              value={segment}
              onChange={(e) => setSegment(e.target.value)}
            >
              <option value="">whole population</option>
              {(segments.data?.data ?? []).map((seg) => (
                <option key={seg} value={seg}>
                  {seg}
                </option>
              ))}
            </select>
          ) : null}
          <button
            type="button"
            disabled={run.isPending}
            onClick={() => run.mutate()}
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
          >
            {run.isPending ? "Running…" : "Run analysis"}
          </button>
        </div>
      </div>
      <ErrorBanner message={error} />
      {result ? (
        <>
          {!result.causal_claim ? (
            <div
              role="alert"
              className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900"
            >
              <strong>Observational — no causal claim.</strong> {result.caveat}
            </div>
          ) : null}
          {result.bandit ? (
            <div className="rounded-md border border-sky-200 bg-sky-50 p-3 text-sm text-sky-900">
              <strong>Bandit suggestion</strong> (advisory — shipping weights is an operator
              decision): on {result.bandit.metric},{" "}
              {Object.entries(result.bandit.suggested_weights_bp)
                .map(([k, v]) => `${k} ${(v / 100).toFixed(1)}%`)
                .join(" / ")}
              {" · p(best): "}
              {Object.entries(result.bandit.p_best)
                .map(([k, v]) => `${k} ${(v * 100).toFixed(1)}%`)
                .join(" / ")}
            </div>
          ) : null}
          {result.power ? (
            <div
              className={`rounded-md border p-3 text-sm ${
                result.power.powered
                  ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                  : "border-amber-200 bg-amber-50 text-amber-900"
              }`}
            >
              <strong>{result.power.powered ? "Powered" : "Underpowered"}</strong> on{" "}
              {result.power.metric_key}: {result.power.min_arm_n.toLocaleString()} /{" "}
              {result.power.required_n_per_arm.toLocaleString()} units per arm (baseline{" "}
              {(result.power.baseline_rate * 100).toFixed(1)}%, MDE{" "}
              {(result.power.mde * 100).toFixed(0)}% relative)
            </div>
          ) : null}
          {result.warnings.map((w) => (
            <div
              key={w}
              className="rounded-md border border-amber-200 bg-amber-50 p-2 text-xs text-amber-800"
            >
              warning: {w}
            </div>
          ))}
          <div className="flex flex-wrap gap-4 text-sm text-slate-600">
            <span>
              engine: <strong>{result.engine}</strong>
            </span>
            <span>
              sequential: <strong>{result.sequential}</strong>
            </span>
            <span>
              control: <strong>{result.control}</strong>
            </span>
            {result.looks ? (
              <span>
                looks:{" "}
                <strong>
                  {result.looks.used}/{result.looks.max}
                </strong>
              </span>
            ) : null}
            <span className="text-xs text-slate-400">
              result hash (for decisions): <code>{result.result_hash}</code>
            </span>
          </div>
          {Object.entries(result.metrics).map(([key, metric]) => (
            <SectionCard key={key} title={`${key} (${metric.role})`}>
              {metric.insufficient_data ? (
                <div className="text-sm text-slate-500">Insufficient data.</div>
              ) : (
                <table className="w-full text-sm">
                  <thead className="text-left text-xs uppercase text-slate-500">
                    <tr>
                      <th className="py-1 pr-3">Variant</th>
                      <th className="py-1 pr-3">Effect (95% CI)</th>
                      <th className="py-1 pr-3">Interval</th>
                      <th className="py-1 pr-3">Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(metric.comparisons ?? {}).map(([variant, c]) => (
                      <tr key={variant} className="border-t align-top">
                        <td className="py-2 pr-3 font-medium">{variant}</td>
                        <td className="py-2 pr-3">
                          {c.insufficient_data ? (
                            <span className="text-slate-500">insufficient data</span>
                          ) : (
                            <>
                              <div>
                                {fmtNum(c.effect)}{" "}
                                {c.relative != null ? (
                                  <span className="text-xs text-slate-500">
                                    ({(c.relative * 100).toFixed(1)}% rel)
                                  </span>
                                ) : null}
                              </div>
                              <div className="text-xs text-slate-500">
                                [{fmtNum((c.ci ?? c.credible_interval)?.[0])},{" "}
                                {fmtNum((c.ci ?? c.credible_interval)?.[1])}]
                              </div>
                              {c.cuped ? (
                                <div className="text-xs text-violet-700">
                                  CUPED
                                  {c.cuped.mode === "multi"
                                    ? ` ×${c.cuped.covariates?.length ?? 0}`
                                    : ""}
                                  : {fmtNum(c.cuped.effect)}
                                  {c.cuped.variance_reduction_pct != null
                                    ? ` (−${c.cuped.variance_reduction_pct.toFixed(0)}% var)`
                                    : ""}
                                  {c.cuped.caveat ? (
                                    <span className="text-slate-500"> — {c.cuped.caveat}</span>
                                  ) : null}
                                </div>
                              ) : null}
                              {c.quantiles
                                ? Object.entries(c.quantiles).map(([prob, q]) => (
                                    <div key={prob} className="text-xs text-teal-700">
                                      p{Math.round(Number(prob) * 100)}: {fmtNum(q.control)} →{" "}
                                      {fmtNum(q.treatment)} ({q.diff >= 0 ? "+" : ""}
                                      {fmtNum(q.diff)})
                                    </div>
                                  ))
                                : null}
                              {c.time_stratified ? (
                                <div className="text-xs text-sky-700">
                                  Time-stratified: {fmtNum(c.time_stratified.effect)} over{" "}
                                  {c.time_stratified.strata} windows
                                </div>
                              ) : null}
                              {c.corpus_prior && c.shrunk_effect != null ? (
                                <div className="text-xs text-amber-700">
                                  Corpus-shrunk: {fmtNum(c.shrunk_effect)} (prior of{" "}
                                  {c.corpus_prior.n_experiments} decided experiments)
                                </div>
                              ) : null}
                            </>
                          )}
                        </td>
                        <td className="py-2 pr-3">
                          {!c.insufficient_data && (c.ci ?? c.credible_interval) ? (
                            <CiBar ci={(c.ci ?? c.credible_interval)!} effect={c.effect ?? 0} />
                          ) : null}
                        </td>
                        <td className="py-2 pr-3 text-xs text-slate-600">
                          {c.p_beat_control != null ? (
                            <>
                              P(beat control) {(c.p_beat_control * 100).toFixed(1)}% · expected loss{" "}
                              {fmtNum(c.expected_loss, 5)}
                            </>
                          ) : (
                            <>
                              {c.always_valid_p != null
                                ? `always-valid p ${fmtNum(c.always_valid_p)}`
                                : c.p != null
                                  ? `p ${fmtNum(c.p)}`
                                  : "—"}
                              {c.boundary_z != null ? (
                                <div>
                                  OF boundary z {fmtNum(c.boundary_z, 2)} ·{" "}
                                  {c.significant_at_boundary ? "significant" : "not significant"}
                                </div>
                              ) : null}
                            </>
                          )}
                          {c.passes_fdr != null ? (
                            <div>{c.passes_fdr ? "passes FDR" : "fails FDR"}</div>
                          ) : null}
                          {c.caveat ? <div className="text-amber-700">{c.caveat}</div> : null}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </SectionCard>
          ))}
        </>
      ) : (
        <div className="text-sm text-slate-500">
          Run the analysis to see effects with confidence intervals. O&apos;Brien-Fleming
          experiments consume one look per run; mSPRT experiments peek freely.
        </div>
      )}
      {(history.data?.data ?? []).length > 0 ? (
        <SectionCard title="Look history (newest first)">
          <ul className="space-y-1 text-xs text-slate-600">
            {(history.data?.data ?? []).map((entry) => (
              <li key={`${entry.result_hash}-${entry.at}`}>
                {entry.at ? new Date(entry.at).toLocaleString() : "—"}
                {entry.look != null ? ` · look ${entry.look}` : ""}
                {entry.automated ? " · automated" : ""} ·{" "}
                <code>{(entry.result_hash ?? "").slice(0, 12)}…</code>
              </li>
            ))}
          </ul>
        </SectionCard>
      ) : null}
    </div>
  );
}
