"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addEdge, applyEdgeChanges, applyNodeChanges } from "@xyflow/react";
import type { Connection, Edge, EdgeChange, Node, NodeChange } from "@xyflow/react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

import { CanvasView } from "./canvas-view";
import { applyStepUpdate, autoLayout, toDefinition, toReactFlow } from "./convert";
import type { StepNodeData } from "./convert";
import { ListView } from "./list-view";
import { StepConfigPanel } from "./step-config-panel";
import type {
  StepDef,
  ValidationErrorItem,
  WorkflowDefinition,
  WorkflowInput,
  WorkflowOutput,
} from "./types";
import { emptyDefinition, IO_TYPES, normalizeDefinition, sanitizeKey } from "./types";

interface PackDetail {
  id: string;
  name: string;
  status: string;
  definition: Record<string, unknown>;
}

interface Capability {
  key: string;
  name: string;
}

export default function WorkflowEditor({ orgId, packId }: { orgId: string; packId: string }) {
  const queryClient = useQueryClient();

  const {
    data: packData,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["workflow-pack", orgId, packId],
    queryFn: () => apiWithAuth<{ data: PackDetail }>(`/orgs/${orgId}/workflow-packs/${packId}`),
  });

  const { data: capsData } = useQuery({
    queryKey: ["capabilities"],
    queryFn: () => apiWithAuth<{ data: Capability[] }>("/capabilities"),
  });
  const capabilities = capsData?.data ?? [];

  const [definition, setDefinition] = useState<WorkflowDefinition | null>(null);
  const [nodes, setNodes] = useState<Node<StepNodeData>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [view, setView] = useState<"canvas" | "list">("canvas");
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);
  const [errors, setErrors] = useState<ValidationErrorItem[]>([]);
  const [dirty, setDirty] = useState(false);
  // Monotonic edit counter — lets a save that succeeds AFTER further edits
  // avoid clearing the dirty flag (the newer edits are still unsaved).
  const editCountRef = useRef(0);
  const savedEditCountRef = useRef(0);
  const markDirty = useCallback(() => {
    editCountRef.current += 1;
    setDirty(true);
  }, []);

  // Real navigation guard while dirty — the badge alone is cosmetic.
  useEffect(() => {
    if (!dirty) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [dirty]);

  // beforeunload only covers hard navigation — client-side <Link> clicks
  // bypass it entirely. Intercept anchor clicks within the editor (capture
  // phase, before Next's router) and confirm when dirty. window.confirm
  // matches how the app confirms elsewhere (fork/remove installation).
  useEffect(() => {
    if (!dirty) return;
    const handler = (e: MouseEvent) => {
      const anchor = (e.target as HTMLElement | null)?.closest?.("a[href]");
      if (!anchor) return;
      if (!window.confirm("You have unsaved changes. Leave without saving?")) {
        e.preventDefault();
        e.stopPropagation();
      }
    };
    document.addEventListener("click", handler, true);
    return () => document.removeEventListener("click", handler, true);
  }, [dirty]);

  // Initialize once from server. DEEP-normalize instead of casting: the
  // backend validates with Pydantic (which fills defaults) but stores the
  // author's RAW dict — so a valid stored definition can omit per-step
  // config/inputs/outputs keys entirely, and ui.positions can hold junk.
  // Top-level-only normalization crashed on `step.inputs.map(...)`.
  useEffect(() => {
    if (packData && definition === null) {
      const def = normalizeDefinition(packData.data.definition ?? {});
      setDefinition(def);
      const rf = toReactFlow(def);
      setNodes(rf.nodes);
      setEdges(rf.edges);
    }
  }, [packData, definition]);

  // Apply a definition update + resync React Flow state
  const applyDefinition = useCallback(
    (def: WorkflowDefinition) => {
      setDefinition(def);
      const rf = toReactFlow(def);
      setNodes(rf.nodes);
      setEdges(rf.edges);
      markDirty();
    },
    [markDirty],
  );

  const currentDefinition = useCallback((): WorkflowDefinition => {
    if (!definition) return emptyDefinition();
    return toDefinition(definition, nodes, edges);
  }, [definition, nodes, edges]);

  const onNodesChange = useCallback(
    (changes: NodeChange<Node<StepNodeData>>[]) => {
      setNodes((nds) => applyNodeChanges(changes, nds));
      // Canvas-level deletion (Backspace/Delete) bypasses deleteStep — clean
      // up dangling edges and workflow outputs pointing at the removed nodes.
      const removedIds = new Set(changes.filter((c) => c.type === "remove").map((c) => c.id));
      if (removedIds.size > 0) {
        setEdges((eds) =>
          eds.filter((e) => !removedIds.has(e.source) && !removedIds.has(e.target)),
        );
        setDefinition((def) =>
          def
            ? {
                ...def,
                steps: def.steps.filter((s) => !removedIds.has(s.id)),
                edges: def.edges.filter(
                  (e) => !removedIds.has(e.from_step) && !removedIds.has(e.to_step),
                ),
                outputs: def.outputs.filter((o) => !removedIds.has(o.from_step)),
              }
            : def,
        );
        setSelectedStepId((sel) => (sel && removedIds.has(sel) ? null : sel));
      }
      if (changes.some((c) => c.type !== "select" && c.type !== "dimensions")) {
        markDirty();
      }
    },
    [markDirty],
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange<Edge>[]) => {
      setEdges((eds) => applyEdgeChanges(changes, eds));
      if (changes.some((c) => c.type !== "select")) markDirty();
    },
    [markDirty],
  );

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
      markDirty();
    },
    [markDirty],
  );

  const updateStep = useCallback(
    (updated: StepDef) => {
      // Cascade port renames/removals to edges + workflow outputs (pure
      // function in convert.ts — see applyStepUpdate for the semantics).
      applyDefinition(applyStepUpdate(currentDefinition(), updated));
    },
    [currentDefinition, applyDefinition],
  );

  const deleteStep = useCallback(
    (stepId: string) => {
      const def = currentDefinition();
      applyDefinition({
        ...def,
        steps: def.steps.filter((s) => s.id !== stepId),
        edges: def.edges.filter((e) => e.from_step !== stepId && e.to_step !== stepId),
        outputs: def.outputs.filter((o) => o.from_step !== stepId),
      });
      setSelectedStepId(null);
    },
    [currentDefinition, applyDefinition],
  );

  const saveMutation = useMutation({
    mutationFn: async () => {
      // Snapshot the edit counter — if more edits land while the save is in
      // flight, onSuccess must NOT clear the dirty flag.
      savedEditCountRef.current = editCountRef.current;
      const def = currentDefinition();
      // Validate first for structured errors (the PUT would 422 with the same
      // details, but the dry-run keeps the flow simple)
      const validation = await apiWithAuth<{
        data: { valid: boolean; errors: ValidationErrorItem[] };
      }>(`/orgs/${orgId}/workflow-packs/validate`, {
        method: "POST",
        body: JSON.stringify({ definition: def }),
      });
      if (!validation.data.valid) {
        setErrors(validation.data.errors);
        throw new ApiError(422, "WF_VALIDATION_FAILED", "Definition has validation errors");
      }
      setErrors([]);
      return apiWithAuth(`/orgs/${orgId}/workflow-packs/${packId}/definition`, {
        method: "PUT",
        body: JSON.stringify({ definition: def }),
      });
    },
    onSuccess: () => {
      // Only clear dirty if nothing changed since the save was snapshotted
      if (editCountRef.current === savedEditCountRef.current) {
        setDirty(false);
      }
      toast.success("Workflow saved");
      queryClient.invalidateQueries({ queryKey: ["workflow-pack", orgId, packId] });
    },
    onError: (err) => {
      toast.error(err instanceof ApiError ? err.message : "Failed to save workflow");
    },
  });

  if (isError) {
    return (
      <div className="space-y-2">
        <p className="text-sm text-red-600">Failed to load this workflow pack.</p>
        <Link
          href={`/dashboard/orgs/${orgId}/workflow-packs`}
          className="text-sm text-[hsl(var(--muted-foreground))] hover:underline"
        >
          ← Back to workflow packs
        </Link>
      </div>
    );
  }
  if (isLoading || !definition) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading editor…</p>;
  }

  const selectedStep =
    selectedStepId != null
      ? (currentDefinition().steps.find((s) => s.id === selectedStepId) ?? null)
      : null;

  const handleErrorClick = (error: ValidationErrorItem) => {
    const match = error.pointer.match(/^\/steps\/(\d+)/);
    const index = match?.[1];
    if (index !== undefined) {
      const def = currentDefinition();
      const step = def.steps[parseInt(index, 10)];
      if (step) setSelectedStepId(step.id);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Link
            href={`/dashboard/orgs/${orgId}/workflow-packs/${packId}`}
            className="text-sm text-[hsl(var(--muted-foreground))] hover:underline"
          >
            ← {packData?.data.name}
          </Link>
          {dirty && (
            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200">
              Unsaved changes
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-md border">
            <button
              onClick={() => setView("canvas")}
              className={`px-3 py-1.5 text-sm ${view === "canvas" ? "bg-[hsl(var(--secondary))]" : ""}`}
            >
              Canvas
            </button>
            <button
              onClick={() => setView("list")}
              className={`px-3 py-1.5 text-sm ${view === "list" ? "bg-[hsl(var(--secondary))]" : ""}`}
            >
              List
            </button>
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => applyDefinition(autoLayout(currentDefinition()))}
          >
            Auto-layout
          </Button>
          <Button size="sm" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : "Save"}
          </Button>
        </div>
      </div>

      {errors.length > 0 && (
        <div
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 p-3 dark:border-red-900 dark:bg-red-950"
        >
          <p className="text-sm font-medium text-red-800 dark:text-red-200">
            {errors.length} validation error{errors.length !== 1 ? "s" : ""}
          </p>
          <ul className="mt-1 space-y-0.5">
            {errors.map((error, i) => (
              <li key={i}>
                <button
                  onClick={() => handleErrorClick(error)}
                  className="text-left text-xs text-red-700 hover:underline dark:text-red-300"
                >
                  <code className="font-mono">{error.code}</code> {error.pointer} — {error.message}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-4">
        <div className="min-w-0 flex-1">
          {view === "canvas" ? (
            <CanvasView
              definition={currentDefinition()}
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onSelectStep={setSelectedStepId}
            />
          ) : (
            <ListView
              definition={currentDefinition()}
              selectedStepId={selectedStepId}
              onSelectStep={setSelectedStepId}
              onChange={applyDefinition}
            />
          )}

          <IOSection definition={currentDefinition()} onChange={applyDefinition} />
        </div>

        {selectedStep && (
          <StepConfigPanel
            // Remount per step: the panel has uncontrolled fields (transform
            // params textarea) whose defaultValue only applies on mount —
            // without the key, switching steps shows the previous step's text.
            key={selectedStep.id}
            step={selectedStep}
            capabilities={capabilities}
            onChange={updateStep}
            onDelete={() => deleteStep(selectedStep.id)}
          />
        )}
      </div>
    </div>
  );
}

// ── Workflow inputs / outputs editors ─────────────────────

function IOSection({
  definition,
  onChange,
}: {
  definition: WorkflowDefinition;
  onChange: (def: WorkflowDefinition) => void;
}) {
  const setInputs = (inputs: WorkflowInput[]) => onChange({ ...definition, inputs });
  const setOutputs = (outputs: WorkflowOutput[]) => onChange({ ...definition, outputs });

  return (
    <div className="mt-4 grid gap-4 lg:grid-cols-2">
      <section className="rounded-lg border p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Workflow Inputs</h2>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              // `_${length+1}` collides after a mid-list delete — probe for
              // the first free key (backend rejects duplicates)
              const taken = new Set(definition.inputs.map((inp) => inp.key));
              let n = definition.inputs.length + 1;
              while (taken.has(`input_${n}`)) n += 1;
              setInputs([
                ...definition.inputs,
                { key: `input_${n}`, type: "text", required: true },
              ]);
            }}
          >
            Add input
          </Button>
        </div>
        <div className="mt-3 space-y-2">
          {definition.inputs.map((input, i) => (
            <div key={i} className="flex flex-wrap items-center gap-1.5">
              <Input
                value={input.key}
                aria-label={`Input key ${i + 1}`}
                onChange={(e) =>
                  setInputs(
                    definition.inputs.map((inp, idx) =>
                      idx === i ? { ...inp, key: sanitizeKey(e.target.value) } : inp,
                    ),
                  )
                }
                className="w-36"
              />
              <select
                value={input.type}
                aria-label={`Input type ${i + 1}`}
                onChange={(e) =>
                  setInputs(
                    definition.inputs.map((inp, idx) =>
                      idx === i ? { ...inp, type: e.target.value } : inp,
                    ),
                  )
                }
                className="rounded border bg-transparent px-2 py-1.5 text-sm"
              >
                {IO_TYPES.map((t) => (
                  <option key={t.type} value={t.type}>
                    {t.type}
                  </option>
                ))}
              </select>
              <label className="flex items-center gap-1 text-xs">
                <input
                  type="checkbox"
                  checked={input.required !== false}
                  onChange={(e) =>
                    setInputs(
                      definition.inputs.map((inp, idx) =>
                        idx === i ? { ...inp, required: e.target.checked } : inp,
                      ),
                    )
                  }
                />
                required
              </label>
              <button
                onClick={() => setInputs(definition.inputs.filter((_, idx) => idx !== i))}
                aria-label={`Remove input ${input.key}`}
                className="rounded px-1.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
              >
                ✕
              </button>
            </div>
          ))}
          {definition.inputs.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No inputs declared.</p>
          )}
        </div>
      </section>

      <section className="rounded-lg border p-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Workflow Outputs</h2>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              const taken = new Set(definition.outputs.map((out) => out.key));
              let n = definition.outputs.length + 1;
              while (taken.has(`output_${n}`)) n += 1;
              setOutputs([
                ...definition.outputs,
                {
                  key: `output_${n}`,
                  type: "image",
                  from_step: definition.steps[0]?.id ?? "",
                  from_port: "",
                },
              ]);
            }}
          >
            Add output
          </Button>
        </div>
        <div className="mt-3 space-y-2">
          {definition.outputs.map((output, i) => {
            const srcStep = definition.steps.find((s) => s.id === output.from_step);
            return (
              <div key={i} className="flex flex-wrap items-center gap-1.5">
                <Input
                  value={output.key}
                  aria-label={`Output key ${i + 1}`}
                  onChange={(e) =>
                    setOutputs(
                      definition.outputs.map((out, idx) =>
                        idx === i ? { ...out, key: sanitizeKey(e.target.value) } : out,
                      ),
                    )
                  }
                  className="w-32"
                />
                <select
                  value={output.from_step}
                  aria-label={`Output source step ${i + 1}`}
                  onChange={(e) =>
                    setOutputs(
                      definition.outputs.map((out, idx) =>
                        idx === i ? { ...out, from_step: e.target.value, from_port: "" } : out,
                      ),
                    )
                  }
                  className="rounded border bg-transparent px-2 py-1.5 text-sm"
                >
                  <option value="">from step…</option>
                  {definition.steps.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
                <select
                  value={output.from_port}
                  aria-label={`Output source port ${i + 1}`}
                  onChange={(e) => {
                    const port = srcStep?.outputs.find((p) => p.port === e.target.value);
                    setOutputs(
                      definition.outputs.map((out, idx) =>
                        idx === i
                          ? { ...out, from_port: e.target.value, type: port?.type ?? out.type }
                          : out,
                      ),
                    );
                  }}
                  className="rounded border bg-transparent px-2 py-1.5 text-sm"
                  disabled={!srcStep}
                >
                  <option value="">port…</option>
                  {(srcStep?.outputs ?? []).map((p) => (
                    <option key={p.port} value={p.port}>
                      {p.port} ({p.type})
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => setOutputs(definition.outputs.filter((_, idx) => idx !== i))}
                  aria-label={`Remove output ${output.key}`}
                  className="rounded px-1.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
                >
                  ✕
                </button>
              </div>
            );
          })}
          {definition.outputs.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No outputs declared.</p>
          )}
        </div>
      </section>
    </div>
  );
}
