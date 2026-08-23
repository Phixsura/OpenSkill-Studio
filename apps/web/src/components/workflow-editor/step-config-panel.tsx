"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import type { PortDef, StepDef } from "./types";
import { IO_TYPES, STEP_TYPES } from "./types";

interface Capability {
  key: string;
  name: string;
}

interface Props {
  step: StepDef;
  onChange: (updated: StepDef) => void;
  onDelete: () => void;
  capabilities: Capability[];
}

const ACCEPT_TYPES = ["image", "video", "audio", "reference_asset"];
const TRANSFORM_OPS = ["crop", "resize", "concat_text", "select_field"];

export function StepConfigPanel({ step, onChange, onDelete, capabilities }: Props) {
  const setConfig = (key: string, value: unknown) =>
    onChange({ ...step, config: { ...step.config, [key]: value } });

  const setPorts = (kind: "inputs" | "outputs", ports: PortDef[]) =>
    onChange({ ...step, [kind]: ports });

  const typeLabel = STEP_TYPES.find((s) => s.type === step.type)?.label ?? step.type;

  return (
    <div className="w-80 shrink-0 space-y-4 overflow-y-auto rounded-lg border bg-[hsl(var(--card))] p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{typeLabel}</h3>
        <button
          onClick={onDelete}
          className="rounded px-2 py-1 text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
        >
          Delete step
        </button>
      </div>
      <p className="text-xs text-[hsl(var(--muted-foreground))]">id: {step.id}</p>

      <div>
        <label htmlFor="step-name" className="block text-sm font-medium">
          Name
        </label>
        <Input
          id="step-name"
          value={step.name}
          maxLength={200}
          onChange={(e) => onChange({ ...step, name: e.target.value })}
          className="mt-1"
        />
      </div>

      {step.type === "instruction" && (
        <div>
          <label htmlFor="cfg-content" className="block text-sm font-medium">
            Instructions
          </label>
          <textarea
            id="cfg-content"
            value={String(step.config.content ?? "")}
            maxLength={4000}
            rows={5}
            onChange={(e) => setConfig("content", e.target.value)}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          />
        </div>
      )}

      {step.type === "prompt_template" && (
        <div>
          <label htmlFor="cfg-template" className="block text-sm font-medium">
            Template
          </label>
          <textarea
            id="cfg-template"
            value={String(step.config.template ?? "")}
            maxLength={4000}
            rows={5}
            onChange={(e) => setConfig("template", e.target.value)}
            className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            placeholder="Photo of {{inputs.product_name}}"
          />
          <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
            {"Reference workflow inputs with {{inputs.key}} and upstream outputs with {{steps.id.outputs.port}}"}
          </p>
        </div>
      )}

      {step.type === "asset_input" && (
        <fieldset>
          <legend className="text-sm font-medium">Accepted types</legend>
          <div className="mt-1 space-y-1">
            {ACCEPT_TYPES.map((t) => {
              const list = (step.config.accept_types as string[]) ?? [];
              return (
                <label key={t} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={list.includes(t)}
                    onChange={(e) =>
                      setConfig(
                        "accept_types",
                        e.target.checked ? [...list, t] : list.filter((x) => x !== t),
                      )
                    }
                  />
                  {t}
                </label>
              );
            })}
          </div>
        </fieldset>
      )}

      {step.type === "transform" && (
        <>
          <div>
            <label htmlFor="cfg-op" className="block text-sm font-medium">
              Operation
            </label>
            <select
              id="cfg-op"
              value={String(step.config.operation ?? "concat_text")}
              onChange={(e) => setConfig("operation", e.target.value)}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            >
              {TRANSFORM_OPS.map((op) => (
                <option key={op} value={op}>
                  {op}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="cfg-params" className="block text-sm font-medium">
              Params (JSON)
            </label>
            <textarea
              id="cfg-params"
              defaultValue={JSON.stringify(step.config.params ?? {}, null, 2)}
              rows={3}
              onBlur={(e) => {
                try {
                  setConfig("params", JSON.parse(e.target.value || "{}"));
                } catch {
                  /* keep previous params on invalid JSON */
                }
              }}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 font-mono text-xs outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            />
          </div>
        </>
      )}

      {step.type === "provider_action" && (
        <>
          <div>
            <label htmlFor="cfg-capability" className="block text-sm font-medium">
              Capability
            </label>
            <select
              id="cfg-capability"
              value={String(step.config.capability ?? "")}
              onChange={(e) => setConfig("capability", e.target.value)}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            >
              <option value="">Select capability…</option>
              {capabilities.map((cap) => (
                <option key={cap.key} value={cap.key}>
                  {cap.name} ({cap.key})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="cfg-features" className="block text-sm font-medium">
              Required features
            </label>
            <Input
              id="cfg-features"
              value={((step.config.required_features as string[]) ?? []).join(", ")}
              onChange={(e) =>
                setConfig(
                  "required_features",
                  e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean),
                )
              }
              placeholder="style_reference, hi_res"
              className="mt-1"
            />
            <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">Comma-separated</p>
          </div>
          <div>
            <label htmlFor="cfg-binding" className="block text-sm font-medium">
              Binding mode
            </label>
            <select
              id="cfg-binding"
              value={String(step.config.binding_mode ?? "auto")}
              onChange={(e) => setConfig("binding_mode", e.target.value)}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            >
              <option value="auto">Auto (cheapest eligible)</option>
              <option value="preferred">Preferred</option>
              <option value="pinned">Pinned (no fallback)</option>
            </select>
          </div>
        </>
      )}

      {step.type === "review_gate" && (
        <>
          <div>
            <label htmlFor="cfg-instructions" className="block text-sm font-medium">
              Review instructions
            </label>
            <textarea
              id="cfg-instructions"
              value={String(step.config.instructions ?? "")}
              maxLength={2000}
              rows={3}
              onChange={(e) => setConfig("instructions", e.target.value)}
              className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            />
          </div>
          <div>
            <label htmlFor="cfg-due" className="block text-sm font-medium">
              Due days (1-30)
            </label>
            <Input
              id="cfg-due"
              type="number"
              min={1}
              max={30}
              value={String(step.config.due_days ?? 7)}
              onChange={(e) => setConfig("due_days", parseInt(e.target.value, 10) || 7)}
              className="mt-1"
            />
          </div>
        </>
      )}

      {step.type === "output" && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Marks final output. Connect upstream ports and declare workflow outputs in
          the Outputs section.
        </p>
      )}

      <PortEditor
        label="Input ports"
        ports={step.inputs}
        onChange={(ports) => setPorts("inputs", ports)}
        showRequired
      />
      <PortEditor
        label="Output ports"
        ports={step.outputs}
        onChange={(ports) => setPorts("outputs", ports)}
      />
    </div>
  );
}

function PortEditor({
  label,
  ports,
  onChange,
  showRequired = false,
}: {
  label: string;
  ports: PortDef[];
  onChange: (ports: PortDef[]) => void;
  showRequired?: boolean;
}) {
  const update = (i: number, patch: Partial<PortDef>) =>
    onChange(ports.map((p, idx) => (idx === i ? { ...p, ...patch } : p)));

  return (
    <div>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{label}</span>
        <Button
          size="sm"
          variant="secondary"
          type="button"
          onClick={() =>
            onChange([...ports, { port: `port_${ports.length + 1}`, type: "text", required: true }])
          }
        >
          Add
        </Button>
      </div>
      <div className="mt-2 space-y-2">
        {ports.map((port, i) => (
          <div key={i} className="flex items-center gap-1">
            <input
              value={port.port}
              onChange={(e) =>
                update(i, {
                  port: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, "_"),
                })
              }
              aria-label={`${label} name ${i + 1}`}
              className="w-24 rounded border bg-transparent px-2 py-1 text-xs"
            />
            <select
              value={port.type}
              onChange={(e) => update(i, { type: e.target.value })}
              aria-label={`${label} type ${i + 1}`}
              className="rounded border bg-transparent px-1 py-1 text-xs"
            >
              {IO_TYPES.map((t) => (
                <option key={t.type} value={t.type}>
                  {t.type}
                </option>
              ))}
            </select>
            {showRequired && (
              <label className="flex items-center gap-1 text-[10px]">
                <input
                  type="checkbox"
                  checked={port.required !== false}
                  onChange={(e) => update(i, { required: e.target.checked })}
                />
                req
              </label>
            )}
            <button
              type="button"
              onClick={() => onChange(ports.filter((_, idx) => idx !== i))}
              aria-label={`Remove ${label.toLowerCase()} ${port.port}`}
              className="rounded px-1.5 text-xs text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
