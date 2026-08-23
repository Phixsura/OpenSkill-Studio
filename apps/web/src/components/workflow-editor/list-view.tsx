"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import type { EdgeDef, WorkflowDefinition } from "./types";
import { COERCIBLE, defaultStep, slugifyStepId, STEP_TYPES } from "./types";

interface Props {
  definition: WorkflowDefinition;
  selectedStepId: string | null;
  onSelectStep: (id: string | null) => void;
  onChange: (def: WorkflowDefinition) => void;
}

/** Keyboard-accessible list alternative to the canvas. */
export function ListView({ definition, selectedStepId, onSelectStep, onChange }: Props) {
  const [newType, setNewType] = useState("prompt_template");
  const [newName, setNewName] = useState("");

  const addStep = () => {
    if (!newName.trim()) return;
    const existing = new Set(definition.steps.map((s) => s.id));
    const id = slugifyStepId(newName, existing);
    const step = defaultStep(newType, id, newName.trim());
    onChange({ ...definition, steps: [...definition.steps, step] });
    setNewName("");
    onSelectStep(id);
  };

  const removeEdge = (edgeId: string) => {
    onChange({ ...definition, edges: definition.edges.filter((e) => e.id !== edgeId) });
  };

  const addEdge = (edge: EdgeDef) => {
    if (definition.edges.some((e) => e.id === edge.id)) return;
    onChange({ ...definition, edges: [...definition.edges, edge] });
  };

  return (
    <div className="space-y-4">
      <ol className="space-y-3">
        {definition.steps.map((step) => {
          const incoming = definition.edges.filter((e) => e.to_step === step.id);
          const typeMeta = STEP_TYPES.find((t) => t.type === step.type);
          return (
            <li
              key={step.id}
              className={`rounded-lg border p-4 ${
                selectedStepId === step.id ? "ring-2 ring-[hsl(var(--ring))]" : ""
              }`}
            >
              <button
                type="button"
                onClick={() => onSelectStep(step.id)}
                className="flex w-full items-center justify-between text-left"
              >
                <div>
                  <span className="font-medium">{step.name}</span>
                  <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                    {step.id}
                  </span>
                </div>
                <span
                  className="rounded-full px-2 py-0.5 text-xs font-medium text-white"
                  style={{ backgroundColor: typeMeta?.color }}
                >
                  {typeMeta?.label ?? step.type}
                </span>
              </button>

              <div className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                in: {step.inputs.map((p) => `${p.port}:${p.type}`).join(", ") || "—"}
                {" · "}
                out: {step.outputs.map((p) => `${p.port}:${p.type}`).join(", ") || "—"}
              </div>

              {step.inputs.length > 0 && (
                <div className="mt-3 border-t pt-3">
                  <p className="text-xs font-medium">Connections in</p>
                  <table className="mt-1 w-full text-xs">
                    <tbody>
                      {incoming.map((edge) => (
                        <tr key={edge.id}>
                          <td className="py-0.5">
                            {edge.from_step}.{edge.from_port} → {edge.to_port}
                          </td>
                          <td className="text-right">
                            <button
                              type="button"
                              onClick={() => removeEdge(edge.id)}
                              className="rounded px-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
                              aria-label={`Remove connection ${edge.id}`}
                            >
                              ✕
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <AddConnectionRow definition={definition} step={step.id} onAdd={addEdge} />
                </div>
              )}
            </li>
          );
        })}
      </ol>

      <div className="flex items-end gap-2 rounded-lg border border-dashed p-4">
        <div>
          <label htmlFor="new-step-type" className="block text-xs font-medium">
            Step type
          </label>
          <select
            id="new-step-type"
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            className="mt-1 rounded-md border bg-transparent px-2 py-1.5 text-sm"
          >
            {STEP_TYPES.map((t) => (
              <option key={t.type} value={t.type}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1">
          <label htmlFor="new-step-name" className="block text-xs font-medium">
            Step name
          </label>
          <Input
            id="new-step-name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addStep())}
            placeholder="Generate key visual"
            className="mt-1"
          />
        </div>
        <Button type="button" size="sm" onClick={addStep} disabled={!newName.trim()}>
          Add step
        </Button>
      </div>
    </div>
  );
}

function AddConnectionRow({
  definition,
  step,
  onAdd,
}: {
  definition: WorkflowDefinition;
  step: string;
  onAdd: (edge: EdgeDef) => void;
}) {
  const target = definition.steps.find((s) => s.id === step);
  const [toPort, setToPort] = useState("");
  const [fromStep, setFromStep] = useState("");
  const [fromPort, setFromPort] = useState("");

  if (!target || target.inputs.length === 0) return null;

  const dstPort = target.inputs.find((p) => p.port === toPort);
  const sourceSteps = definition.steps.filter((s) => s.id !== step);
  const source = definition.steps.find((s) => s.id === fromStep);
  const compatiblePorts = (source?.outputs ?? []).filter(
    (p) => !dstPort || (COERCIBLE[p.type]?.includes(dstPort.type) ?? false),
  );

  const canAdd = toPort && fromStep && fromPort;

  return (
    <div className="mt-2 flex flex-wrap items-center gap-1 text-xs">
      <select
        value={toPort}
        onChange={(e) => {
          setToPort(e.target.value);
          setFromPort("");
        }}
        aria-label="Target input port"
        className="rounded border bg-transparent px-1 py-1"
      >
        <option value="">into port…</option>
        {target.inputs.map((p) => (
          <option key={p.port} value={p.port}>
            {p.port} ({p.type})
          </option>
        ))}
      </select>
      <select
        value={fromStep}
        onChange={(e) => {
          setFromStep(e.target.value);
          setFromPort("");
        }}
        aria-label="Source step"
        className="rounded border bg-transparent px-1 py-1"
      >
        <option value="">from step…</option>
        {sourceSteps.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name}
          </option>
        ))}
      </select>
      <select
        value={fromPort}
        onChange={(e) => setFromPort(e.target.value)}
        aria-label="Source output port"
        className="rounded border bg-transparent px-1 py-1"
        disabled={!fromStep}
      >
        <option value="">port…</option>
        {compatiblePorts.map((p) => (
          <option key={p.port} value={p.port}>
            {p.port} ({p.type})
          </option>
        ))}
      </select>
      <button
        type="button"
        disabled={!canAdd}
        onClick={() =>
          canAdd &&
          onAdd({
            id: `e_${fromStep}_${fromPort}_${step}_${toPort}`,
            from_step: fromStep,
            from_port: fromPort,
            to_step: step,
            to_port: toPort,
          })
        }
        className="rounded border px-2 py-1 disabled:opacity-50"
      >
        Connect
      </button>
    </div>
  );
}
