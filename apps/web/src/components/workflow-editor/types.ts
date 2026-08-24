// Workflow editor shared constants and types.
// Keep in sync with apps/api/app/schemas/workflow_definition.py
// (STEP_TYPES, IO_TYPES, COERCIBLE must mirror the backend exactly).

export const STEP_TYPES: { type: string; label: string; color: string }[] = [
  { type: "instruction", label: "Instruction", color: "#64748b" },
  { type: "prompt_template", label: "Prompt Template", color: "#8b5cf6" },
  { type: "asset_input", label: "Asset Input", color: "#0ea5e9" },
  { type: "transform", label: "Transform", color: "#f59e0b" },
  { type: "provider_action", label: "Provider Action", color: "#10b981" },
  { type: "review_gate", label: "Review Gate", color: "#ef4444" },
  { type: "output", label: "Output", color: "#334155" },
];

export const IO_TYPES: { type: string; color: string }[] = [
  { type: "text", color: "#94a3b8" },
  { type: "prompt", color: "#8b5cf6" },
  { type: "image", color: "#0ea5e9" },
  { type: "video", color: "#f43f5e" },
  { type: "audio", color: "#f59e0b" },
  { type: "reference_asset", color: "#14b8a6" },
  { type: "json", color: "#a3a3a3" },
  { type: "selection", color: "#eab308" },
];

// Automatic coercion matrix: identity + prompt↔text ONLY.
// Everything else needs an explicit transform step.
export const COERCIBLE: Record<string, string[]> = {
  text: ["text", "prompt"],
  prompt: ["prompt", "text"],
  image: ["image"],
  video: ["video"],
  audio: ["audio"],
  reference_asset: ["reference_asset"],
  json: ["json"],
  selection: ["selection"],
};

export function stepColor(type: string): string {
  return STEP_TYPES.find((s) => s.type === type)?.color ?? "#64748b";
}

export function ioColor(type: string): string {
  return IO_TYPES.find((t) => t.type === type)?.color ?? "#94a3b8";
}

export interface PortDef {
  port: string;
  type: string;
  required?: boolean;
  options?: string[] | null;
}

export interface StepDef {
  id: string;
  type: string;
  name: string;
  config: Record<string, unknown>;
  inputs: PortDef[];
  outputs: PortDef[];
}

export interface EdgeDef {
  id: string;
  from_step: string;
  from_port: string;
  to_step: string;
  to_port: string;
}

export interface WorkflowInput {
  key: string;
  type: string;
  label?: string | null;
  required?: boolean;
  default?: string | null;
  options?: string[] | null;
}

export interface WorkflowOutput {
  key: string;
  type: string;
  from_step: string;
  from_port: string;
}

export interface WorkflowDefinition {
  schema_version: number;
  inputs: WorkflowInput[];
  outputs: WorkflowOutput[];
  steps: StepDef[];
  edges: EdgeDef[];
  ui: { positions?: Record<string, [number, number]> };
}

export interface ValidationErrorItem {
  code: string;
  pointer: string;
  message: string;
  meta?: Record<string, unknown> | null;
}

export function emptyDefinition(): WorkflowDefinition {
  return { schema_version: 1, inputs: [], outputs: [], steps: [], edges: [], ui: {} };
}

/** Validate a ui.positions entry into [x, y] numbers, or null if malformed.
 * The ui block is excluded from backend validation (any dict is storable),
 * so positions can legitimately contain garbage. */
export function normalizePosition(v: unknown): [number, number] | null {
  if (Array.isArray(v) && v.length >= 2) {
    const x = Number(v[0]);
    const y = Number(v[1]);
    if (Number.isFinite(x) && Number.isFinite(y)) return [x, y];
  }
  return null;
}

/** Deep-normalize a raw stored definition. The backend validates with
 * Pydantic (which FILLS defaults) but stores the author's RAW dict — so a
 * perfectly valid stored definition can omit defaulted keys like
 * step.config/inputs/outputs or carry arbitrary junk in ui.positions.
 * Top-level-only normalization crashes on `step.inputs.map(...)`. */
export function normalizeDefinition(raw: unknown): WorkflowDefinition {
  const r = (raw && typeof raw === "object" ? raw : {}) as Record<string, unknown>;
  const steps: StepDef[] = (Array.isArray(r.steps) ? r.steps : [])
    .filter((s): s is Record<string, unknown> => !!s && typeof s === "object")
    .map((s) => ({
      ...(s as unknown as StepDef),
      id: typeof s.id === "string" ? s.id : "",
      type: typeof s.type === "string" ? s.type : "instruction",
      name: typeof s.name === "string" ? s.name : "",
      config: s.config && typeof s.config === "object" ? (s.config as Record<string, unknown>) : {},
      inputs: Array.isArray(s.inputs) ? (s.inputs as PortDef[]) : [],
      outputs: Array.isArray(s.outputs) ? (s.outputs as PortDef[]) : [],
    }));
  const rawUi = r.ui && typeof r.ui === "object" ? (r.ui as Record<string, unknown>) : {};
  const rawPositions =
    rawUi.positions && typeof rawUi.positions === "object"
      ? (rawUi.positions as Record<string, unknown>)
      : {};
  const positions: Record<string, [number, number]> = {};
  for (const [id, pos] of Object.entries(rawPositions)) {
    const norm = normalizePosition(pos);
    if (norm) positions[id] = norm;
  }
  return {
    schema_version: typeof r.schema_version === "number" ? r.schema_version : 1,
    inputs: Array.isArray(r.inputs) ? (r.inputs as WorkflowInput[]) : [],
    outputs: Array.isArray(r.outputs) ? (r.outputs as WorkflowOutput[]) : [],
    steps,
    edges: Array.isArray(r.edges) ? (r.edges as EdgeDef[]) : [],
    ui: { ...rawUi, positions },
  };
}

/** Sanitize a user-typed input/output/port key toward the backend regex
 * ^[a-z][a-z0-9_]{0,63}$ — lowercase, replace illegal chars, strip leading
 * digits/underscores (a leading digit can never become valid), cap length. */
export function sanitizeKey(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9_]/g, "_")
    .replace(/^[^a-z]+/, "")
    .slice(0, 64);
}

/** Generate a valid step id slug from a display name (backend regex: ^[a-z][a-z0-9_]{0,63}$). */
export function slugifyStepId(name: string, existing: Set<string>): string {
  let slug = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 60);
  if (!slug || /^[0-9]/.test(slug)) slug = `s_${slug}`;
  let candidate = slug;
  let n = 2;
  while (existing.has(candidate)) {
    candidate = `${slug}_${n}`;
    n += 1;
  }
  return candidate;
}

/** Default ports per step type for newly added steps. */
export function defaultStep(type: string, id: string, name: string): StepDef {
  const base: StepDef = { id, type, name, config: {}, inputs: [], outputs: [] };
  switch (type) {
    case "instruction":
      return { ...base, config: { content: "" } };
    case "prompt_template":
      return {
        ...base,
        config: { template: "" },
        outputs: [{ port: "prompt", type: "prompt" }],
      };
    case "asset_input":
      return {
        ...base,
        config: { accept_types: ["image"] },
        outputs: [{ port: "asset", type: "image" }],
      };
    case "transform":
      return {
        ...base,
        config: { operation: "concat_text", params: {} },
        inputs: [{ port: "input", type: "text" }],
        outputs: [{ port: "result", type: "text" }],
      };
    case "provider_action":
      return {
        ...base,
        config: { capability: "", required_features: [], binding_mode: "auto" },
        inputs: [{ port: "prompt", type: "prompt" }],
        outputs: [{ port: "result", type: "image" }],
      };
    case "review_gate":
      return {
        ...base,
        config: { instructions: "", due_days: 7 },
        inputs: [{ port: "subject", type: "image" }],
        outputs: [
          { port: "decision", type: "selection" },
          { port: "passed", type: "image" },
        ],
      };
    case "output":
      return { ...base, inputs: [{ port: "final", type: "image" }] };
    default:
      return base;
  }
}
