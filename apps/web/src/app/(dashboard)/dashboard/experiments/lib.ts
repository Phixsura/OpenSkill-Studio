/** Shared types & vocabularies for the Experiment Console (ADR-017 Part L).
 *
 * Vocabularies mirror apps/api/app/experiments/security.py — parity-guarded
 * by tests/test_exp_web_parity.py on the backend side.
 */

export const EXPERIMENT_STATUSES = [
  "draft",
  "review",
  "scheduled",
  "running",
  "paused",
  "completed",
  "analyzed",
  "promoted",
  "rejected",
  "archived",
] as const;

export const EXPERIMENT_DOMAINS = [
  "learning",
  "assessment",
  "workflow",
  "matching",
  "marketplace",
  "operational",
  "talent_flow",
] as const;

export const UNIT_TYPES = [
  "user",
  "cohort",
  "organization",
  "workflow_installation",
  "project",
  "provider_offering",
  "tenant",
] as const;

export const RISK_CLASSES = ["low", "medium", "high"] as const;
export const STATS_ENGINES = ["frequentist", "bayesian"] as const;
export const DESIGNS = ["parallel", "cluster", "switchback"] as const;
export const ALLOCATION_MODES = ["fixed", "bandit"] as const;
export const SEQUENTIAL_METHODS = ["none", "obrien_fleming", "msprt"] as const;
export const ANALYSIS_TYPES = ["randomized", "observational"] as const;
export const DECISIONS = ["promote", "reject", "inconclusive", "extend"] as const;
export const PROMOTION_STATUSES = ["draft", "approved", "applying", "applied", "rejected"] as const;
export const PROMOTION_TARGET_TYPES = [
  "learning_path",
  "pack_recommendation",
  "workflow_binding",
  "matching_config",
  "eco_rollout_policy",
  "pricing_presentation",
] as const;

// §5 v2 launch checklist — mirrors security.LAUNCH_CHECKLIST_KEYS (parity-
// guarded); domains touching learners/talent add the ethics screen.
export const LAUNCH_CHECKLIST_KEYS = [
  "hypothesis_peer_checked",
  "power_computed",
  "metrics_reviewed",
  "rollback_owner_named",
] as const;
export const ETHICS_CHECKLIST_DOMAINS = ["learning", "assessment", "talent_flow"] as const;
export const ETHICS_CHECKLIST_KEY = "ethics_screened";

export const CHECKLIST_LABELS: Record<string, string> = {
  hypothesis_peer_checked: "Hypothesis peer-checked",
  power_computed: "Power / sample size computed",
  metrics_reviewed: "Metrics & guardrails reviewed",
  rollback_owner_named: "Rollback owner named",
  ethics_screened: "Ethics screen completed (learner/talent domain)",
};

// Mirrors the backend state machine (_ALLOWED) so the console only offers
// legal transitions; the server re-validates every one.
export const ALLOWED_TRANSITIONS: Record<string, string[]> = {
  draft: ["review", "archived"],
  review: ["draft", "scheduled", "archived"],
  scheduled: ["running", "archived"],
  running: ["paused", "completed", "archived"],
  paused: ["running", "completed", "archived"],
  completed: ["analyzed", "archived"],
  analyzed: ["promoted", "rejected", "archived"],
  promoted: [],
  rejected: [],
  archived: [],
};

export const STATUS_STYLES: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  review: "bg-amber-100 text-amber-800",
  scheduled: "bg-sky-100 text-sky-800",
  running: "bg-emerald-100 text-emerald-800",
  paused: "bg-orange-100 text-orange-800",
  completed: "bg-indigo-100 text-indigo-800",
  analyzed: "bg-violet-100 text-violet-800",
  promoted: "bg-green-100 text-green-800",
  rejected: "bg-rose-100 text-rose-800",
  archived: "bg-slate-200 text-slate-500",
  // promotion drafts
  approved: "bg-sky-100 text-sky-800",
  applied: "bg-green-100 text-green-800",
  // guardrail actions
  alerted: "bg-amber-100 text-amber-800",
};

export interface Experiment {
  id: string;
  key: string;
  title: string;
  domain: string;
  scope_org_id: string | null;
  layer_key: string;
  status: string;
  current_version: number;
  owner_user_id: string;
  risk_class: string;
  ramp_bp: number;
  holdout_bp: number;
  started_at: string | null;
  ended_at: string | null;
  analysis_close_at: string | null;
  created_at: string;
}

export interface GuardrailEvent {
  id: string;
  guardrail_key: string;
  metric_key: string | null;
  observed: number | null;
  threshold: number | null;
  action: string;
  auto: boolean;
  detail: Record<string, unknown>;
  created_at: string;
}

export interface MetricSnapshot {
  id: string;
  metric_key: string;
  variant_key: string;
  segment?: string;
  window_start: string;
  window_end: string;
  n: number;
  numerator: number | null;
  denominator: number | null;
  sum_value: number | null;
  provenance: { query_version?: number; source?: string };
  computed_at: string;
}

export interface DecisionRecord {
  id: string;
  experiment_id: string;
  decision: string;
  summary: string;
  domain: string;
  analysis_type: string;
  analysis_result_hash: string;
  approver_user_id: string;
  guardrail_outcome: { clean?: boolean };
  created_at: string;
}

export interface PromotionDraft {
  id: string;
  decision_record_id: string;
  target_type: string;
  target_ref: string;
  status: string;
  applied_ref: string | null;
  apply_error: string | null;
  created_at: string;
}

export function fmtDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export function fmtPct(bp: number): string {
  return `${(bp / 100).toFixed(bp % 100 === 0 ? 0 : 2)}%`;
}

export function fmtNum(value: number | null | undefined, digits = 4): string {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(digits);
}
