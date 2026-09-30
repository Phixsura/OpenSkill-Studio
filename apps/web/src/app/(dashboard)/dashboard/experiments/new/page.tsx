"use client";
/** Experiment builder (ADR-017 Part L): basics → variants → metrics →
 * guardrails → engine. Creates the experiment, then version 1 of the
 * immutable spec, then routes to the detail page. The server re-validates
 * everything (ethics gates, weights, control uniqueness). */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ApiError, apiWithAuth } from "@/lib/api";
import { ErrorBanner, ExperimentsNav, SectionCard } from "../components";
import {
  ALLOCATION_MODES,
  ANALYSIS_TYPES,
  DESIGNS,
  EXPERIMENT_DOMAINS,
  RISK_CLASSES,
  SEQUENTIAL_METHODS,
  STATS_ENGINES,
  UNIT_TYPES,
} from "../lib";

interface VariantRow {
  key: string;
  name: string;
  weight_bp: number;
  is_control: boolean;
  config: string;
}

interface Layer {
  id: string;
  key: string;
  domain: string;
}

export default function NewExperimentPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [basics, setBasics] = useState({
    key: "",
    title: "",
    domain: "learning",
    layer_key: "",
    risk_class: "medium",
    holdout_bp: 0,
  });
  const [spec, setSpec] = useState({
    hypothesis: "",
    unit_type: "user",
    stats_engine: "frequentist",
    sequential: "msprt",
    analysis_type: "randomized",
    primary_metrics: "exposure_rate",
    secondary_metrics: "",
    guardrail_metric: "cost_usd",
    guardrail_op: "lte",
    guardrail_threshold: "100",
    guardrail_window_hours: "24",
    design: "parallel",
    allocation_mode: "fixed",
    switchback_window_minutes: "1440",
    switchback_washout_minutes: "0",
  });
  const [variants, setVariants] = useState<VariantRow[]>([
    { key: "control", name: "Control", weight_bp: 5000, is_control: true, config: "{}" },
    { key: "treatment", name: "Treatment", weight_bp: 5000, is_control: false, config: "{}" },
  ]);

  const layers = useQuery({
    queryKey: ["experiment-layers"],
    queryFn: () => apiWithAuth<{ data: Layer[] }>("/experiments/layers"),
  });
  const domainLayers = (layers.data?.data ?? []).filter((l) => l.domain === basics.domain);

  const weightTotal = variants.reduce((sum, v) => sum + Number(v.weight_bp || 0), 0);

  const create = useMutation({
    mutationFn: async () => {
      const created = await apiWithAuth<{ data: { id: string } }>("/experiments", {
        method: "POST",
        body: JSON.stringify(basics),
      });
      let parsedVariants;
      try {
        parsedVariants = variants.map((v) => ({
          key: v.key,
          name: v.name,
          weight_bp: Number(v.weight_bp),
          is_control: v.is_control,
          config: JSON.parse(v.config || "{}"),
        }));
        const specBody = {
          hypothesis: spec.hypothesis,
          unit_type: spec.unit_type,
          variants: parsedVariants,
          metrics: {
            primary: spec.primary_metrics
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
            secondary: spec.secondary_metrics
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
            guardrails: spec.guardrail_metric
              ? [
                  {
                    metric_key: spec.guardrail_metric,
                    op: spec.guardrail_op,
                    threshold: Number(spec.guardrail_threshold),
                    window_hours: Number(spec.guardrail_window_hours),
                  },
                ]
              : [],
          },
          stats_engine: spec.stats_engine,
          sequential: spec.sequential,
          analysis_type: spec.analysis_type,
          design: spec.design,
          allocation_mode: spec.allocation_mode,
          ...(spec.design === "switchback"
            ? {
                switchback: {
                  switch_unit: "platform_window",
                  window_minutes: Number(spec.switchback_window_minutes),
                  washout_minutes: Number(spec.switchback_washout_minutes),
                },
              }
            : {}),
        };
        await apiWithAuth(`/experiments/${created.data.id}/versions`, {
          method: "POST",
          body: JSON.stringify({ spec: specBody }),
        });
      } catch (versionError) {
        // Self-heal: a created-but-spec-less draft would hold the (live-
        // unique) key hostage — archive the orphan before surfacing the error
        await apiWithAuth(`/experiments/${created.data.id}/transition`, {
          method: "POST",
          body: JSON.stringify({ to_status: "archived", reason: "builder spec failed" }),
        }).catch(() => {});
        throw versionError;
      }
      return created.data.id;
    },
    onSuccess: (id) => router.push(`/dashboard/experiments/${id}`),
    onError: (e) => setError(e instanceof ApiError ? e.message : "Failed to create experiment"),
  });

  const input = "w-full rounded-md border px-2 py-1.5 text-sm";
  const label = "block text-xs font-medium text-slate-600";

  return (
    <div className="space-y-6 p-6">
      <ExperimentsNav />
      <h1 className="text-xl font-semibold">New experiment</h1>
      <ErrorBanner message={error} />

      <SectionCard title="1 · Basics">
        <div className="grid gap-3 md:grid-cols-3">
          <div>
            <label className={label} htmlFor="exp-key">
              Key (slug)
            </label>
            <input
              id="exp-key"
              className={input}
              value={basics.key}
              onChange={(e) => setBasics({ ...basics, key: e.target.value })}
              placeholder="rubric-wording-b"
            />
          </div>
          <div>
            <label className={label} htmlFor="exp-title">
              Title
            </label>
            <input
              id="exp-title"
              className={input}
              value={basics.title}
              onChange={(e) => setBasics({ ...basics, title: e.target.value })}
            />
          </div>
          <div>
            <label className={label} htmlFor="exp-domain">
              Domain
            </label>
            <select
              id="exp-domain"
              className={input}
              value={basics.domain}
              onChange={(e) => setBasics({ ...basics, domain: e.target.value, layer_key: "" })}
            >
              {EXPERIMENT_DOMAINS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="exp-layer">
              Layer (mutual exclusion)
            </label>
            <select
              id="exp-layer"
              className={input}
              value={basics.layer_key}
              onChange={(e) => setBasics({ ...basics, layer_key: e.target.value })}
            >
              <option value="">select layer…</option>
              {domainLayers.map((l) => (
                <option key={l.id} value={l.key}>
                  {l.key}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="exp-risk">
              Risk class
            </label>
            <select
              id="exp-risk"
              className={input}
              value={basics.risk_class}
              onChange={(e) => setBasics({ ...basics, risk_class: e.target.value })}
            >
              {RISK_CLASSES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="exp-holdout">
              Holdout (bp, 0-1000)
            </label>
            <input
              id="exp-holdout"
              type="number"
              className={input}
              value={basics.holdout_bp}
              onChange={(e) => setBasics({ ...basics, holdout_bp: Number(e.target.value) })}
            />
          </div>
        </div>
      </SectionCard>

      <SectionCard title="2 · Hypothesis & unit">
        <div className="grid gap-3 md:grid-cols-2">
          <div className="md:col-span-2">
            <label className={label} htmlFor="exp-hypothesis">
              Hypothesis
            </label>
            <textarea
              id="exp-hypothesis"
              className={input}
              rows={2}
              value={spec.hypothesis}
              onChange={(e) => setSpec({ ...spec, hypothesis: e.target.value })}
            />
          </div>
          <div>
            <label className={label} htmlFor="exp-unit">
              Randomization unit
            </label>
            <select
              id="exp-unit"
              className={input}
              value={spec.unit_type}
              onChange={(e) => setSpec({ ...spec, unit_type: e.target.value })}
            >
              {UNIT_TYPES.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="3 · Variants"
        actions={
          <span
            className={`text-xs ${weightTotal === 10000 ? "text-emerald-600" : "text-rose-600"}`}
          >
            weights: {weightTotal}/10000
          </span>
        }
      >
        <div className="space-y-2">
          {variants.map((variant, i) => (
            <div key={i} className="grid gap-2 md:grid-cols-5">
              <input
                aria-label={`variant ${i} key`}
                className={input}
                value={variant.key}
                onChange={(e) =>
                  setVariants(variants.map((v, j) => (j === i ? { ...v, key: e.target.value } : v)))
                }
              />
              <input
                aria-label={`variant ${i} name`}
                className={input}
                value={variant.name}
                onChange={(e) =>
                  setVariants(
                    variants.map((v, j) => (j === i ? { ...v, name: e.target.value } : v)),
                  )
                }
              />
              <input
                aria-label={`variant ${i} weight`}
                type="number"
                className={input}
                value={variant.weight_bp}
                onChange={(e) =>
                  setVariants(
                    variants.map((v, j) =>
                      j === i ? { ...v, weight_bp: Number(e.target.value) } : v,
                    ),
                  )
                }
              />
              <input
                aria-label={`variant ${i} config`}
                className={input}
                value={variant.config}
                placeholder='{"config": "json"}'
                onChange={(e) =>
                  setVariants(
                    variants.map((v, j) => (j === i ? { ...v, config: e.target.value } : v)),
                  )
                }
              />
              <label className="flex items-center gap-1 text-xs text-slate-600">
                <input
                  type="radio"
                  name="control"
                  checked={variant.is_control}
                  onChange={() =>
                    setVariants(variants.map((v, j) => ({ ...v, is_control: j === i })))
                  }
                />
                control
              </label>
            </div>
          ))}
          <button
            type="button"
            className="rounded-md border px-2 py-1 text-xs"
            onClick={() =>
              setVariants([
                ...variants,
                {
                  key: `variant-${variants.length}`,
                  name: "",
                  weight_bp: 0,
                  is_control: false,
                  config: "{}",
                },
              ])
            }
          >
            + variant
          </button>
        </div>
      </SectionCard>

      <SectionCard title="4 · Metrics & guardrails">
        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <label className={label} htmlFor="exp-primary">
              Primary metrics (comma-separated keys)
            </label>
            <input
              id="exp-primary"
              className={input}
              value={spec.primary_metrics}
              onChange={(e) => setSpec({ ...spec, primary_metrics: e.target.value })}
            />
          </div>
          <div>
            <label className={label} htmlFor="exp-secondary">
              Secondary metrics
            </label>
            <input
              id="exp-secondary"
              className={input}
              value={spec.secondary_metrics}
              onChange={(e) => setSpec({ ...spec, secondary_metrics: e.target.value })}
            />
          </div>
          <div>
            <label className={label} htmlFor="exp-guardrail">
              Guardrail metric
            </label>
            <input
              id="exp-guardrail"
              className={input}
              value={spec.guardrail_metric}
              onChange={(e) => setSpec({ ...spec, guardrail_metric: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className={label} htmlFor="exp-gop">
                Op
              </label>
              <select
                id="exp-gop"
                className={input}
                value={spec.guardrail_op}
                onChange={(e) => setSpec({ ...spec, guardrail_op: e.target.value })}
              >
                <option value="lte">lte</option>
                <option value="gte">gte</option>
              </select>
            </div>
            <div>
              <label className={label} htmlFor="exp-gthr">
                Threshold
              </label>
              <input
                id="exp-gthr"
                className={input}
                value={spec.guardrail_threshold}
                onChange={(e) => setSpec({ ...spec, guardrail_threshold: e.target.value })}
              />
            </div>
            <div>
              <label className={label} htmlFor="exp-gwin">
                Window (h)
              </label>
              <input
                id="exp-gwin"
                className={input}
                value={spec.guardrail_window_hours}
                onChange={(e) => setSpec({ ...spec, guardrail_window_hours: e.target.value })}
              />
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="5 · Analysis engine">
        <div className="grid gap-3 md:grid-cols-3">
          <div>
            <label className={label} htmlFor="exp-design">
              Design
            </label>
            <select
              id="exp-design"
              className={input}
              value={spec.design}
              onChange={(e) => setSpec({ ...spec, design: e.target.value })}
            >
              {DESIGNS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="exp-alloc">
              Allocation
            </label>
            <select
              id="exp-alloc"
              className={input}
              value={spec.allocation_mode}
              onChange={(e) => setSpec({ ...spec, allocation_mode: e.target.value })}
            >
              {ALLOCATION_MODES.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
          {spec.design === "switchback" ? (
            <>
              <div>
                <label className={label} htmlFor="exp-sb-window">
                  Switch window (minutes)
                </label>
                <input
                  id="exp-sb-window"
                  type="number"
                  className={input}
                  value={spec.switchback_window_minutes}
                  onChange={(e) => setSpec({ ...spec, switchback_window_minutes: e.target.value })}
                />
              </div>
              <div>
                <label className={label} htmlFor="exp-sb-washout">
                  Washout (minutes)
                </label>
                <input
                  id="exp-sb-washout"
                  type="number"
                  className={input}
                  value={spec.switchback_washout_minutes}
                  onChange={(e) => setSpec({ ...spec, switchback_washout_minutes: e.target.value })}
                />
              </div>
            </>
          ) : null}
          <div>
            <label className={label} htmlFor="exp-engine">
              Stats engine
            </label>
            <select
              id="exp-engine"
              className={input}
              value={spec.stats_engine}
              onChange={(e) => setSpec({ ...spec, stats_engine: e.target.value })}
            >
              {STATS_ENGINES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="exp-seq">
              Sequential monitoring
            </label>
            <select
              id="exp-seq"
              className={input}
              value={spec.sequential}
              onChange={(e) => setSpec({ ...spec, sequential: e.target.value })}
            >
              {SEQUENTIAL_METHODS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="exp-atype">
              Analysis type
            </label>
            <select
              id="exp-atype"
              className={input}
              value={spec.analysis_type}
              onChange={(e) => setSpec({ ...spec, analysis_type: e.target.value })}
            >
              {ANALYSIS_TYPES.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
            {spec.analysis_type === "observational" ? (
              <p className="mt-1 text-xs text-amber-700">
                Observational analyses never claim causality and cannot promote.
              </p>
            ) : null}
          </div>
        </div>
      </SectionCard>

      <button
        type="button"
        disabled={create.isPending}
        onClick={() => create.mutate()}
        className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        Create experiment
      </button>
    </div>
  );
}
