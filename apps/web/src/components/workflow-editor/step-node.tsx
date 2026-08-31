"use client";

import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";

import type { StepNodeData } from "./convert";
import { ioColor, stepColor, STEP_TYPES } from "./types";

export function StepNode({ data, selected }: NodeProps & { data: StepNodeData }) {
  const step = data.step;
  const color = stepColor(step.type);
  const label = STEP_TYPES.find((s) => s.type === step.type)?.label ?? step.type;

  return (
    <div
      className={`min-w-[220px] rounded-lg border bg-[hsl(var(--card))] shadow-sm ${
        selected ? "ring-2 ring-[hsl(var(--ring))]" : ""
      }`}
    >
      <div
        className="rounded-t-lg px-3 py-1.5 text-xs font-medium text-white"
        style={{ backgroundColor: color }}
      >
        {label}
      </div>
      <div className="px-3 py-2">
        <p className="text-sm font-semibold">{step.name}</p>
        <p className="text-xs text-[hsl(var(--muted-foreground))]">{step.id}</p>
      </div>

      {/* Input handles (left) */}
      {step.inputs.map((port, i) => (
        <Handle
          key={`in-${port.port}`}
          type="target"
          position={Position.Left}
          id={port.port}
          style={{
            top: 44 + i * 22,
            width: 10,
            height: 10,
            backgroundColor: ioColor(port.type),
          }}
        />
      ))}
      {step.inputs.length > 0 && (
        <div className="border-t px-3 py-1">
          {step.inputs.map((port) => (
            <div
              key={port.port}
              className="flex items-center gap-1 text-[10px] text-[hsl(var(--muted-foreground))]"
            >
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ backgroundColor: ioColor(port.type) }}
              />
              ← {port.port}: {port.type}
              {port.required === false ? " (optional)" : ""}
            </div>
          ))}
        </div>
      )}

      {/* Output handles (right) */}
      {step.outputs.map((port, i) => (
        <Handle
          key={`out-${port.port}`}
          type="source"
          position={Position.Right}
          id={port.port}
          style={{
            top: 44 + i * 22,
            width: 10,
            height: 10,
            backgroundColor: ioColor(port.type),
          }}
        />
      ))}
      {step.outputs.length > 0 && (
        <div className="border-t px-3 py-1">
          {step.outputs.map((port) => (
            <div
              key={port.port}
              className="flex items-center justify-end gap-1 text-[10px] text-[hsl(var(--muted-foreground))]"
            >
              {port.port}: {port.type} →
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ backgroundColor: ioColor(port.type) }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
