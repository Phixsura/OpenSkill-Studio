"use client";

import { useState } from "react";

interface ResourceUsage {
  cpu_seconds: number;
  wall_seconds: number;
  memory_mb: number;
  network_egress_mb: number;
}

interface SandboxExecution {
  id: string;
  app_name: string;
  status: "running" | "completed" | "killed" | "failed" | "timeout";
  started_at: string;
  ended_at: string | null;
  duration_ms: number;
  resources: ResourceUsage;
  exit_code: number | null;
  error: string | null;
  violations: string[];
}

interface SandboxExecutionLogProps {
  executions: SandboxExecution[];
  totalCount: number;
  budgetUsed: number;
  budgetLimit: number;
}

const STATUS_MAP: Record<string, { label: string; color: string; bg: string }> = {
  running: {
    label: "Running",
    color: "text-blue-700 dark:text-blue-300",
    bg: "bg-blue-100 dark:bg-blue-900/30",
  },
  completed: {
    label: "Completed",
    color: "text-green-700 dark:text-green-300",
    bg: "bg-green-100 dark:bg-green-900/30",
  },
  killed: {
    label: "Killed",
    color: "text-red-700 dark:text-red-300",
    bg: "bg-red-100 dark:bg-red-900/30",
  },
  failed: {
    label: "Failed",
    color: "text-red-700 dark:text-red-300",
    bg: "bg-red-100 dark:bg-red-900/30",
  },
  timeout: {
    label: "Timeout",
    color: "text-orange-700 dark:text-orange-300",
    bg: "bg-orange-100 dark:bg-orange-900/30",
  },
};

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return iso;
  }
}

function ResourceBar({
  label,
  value,
  max,
  unit,
}: {
  label: string;
  value: number;
  max: number;
  unit: string;
}) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  const warn = pct > 80;
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-16 text-gray-500">{label}</span>
      <div className="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-full rounded-full ${warn ? "bg-red-500" : "bg-blue-500"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`w-20 text-right ${warn ? "font-medium text-red-600" : "text-gray-500"}`}>
        {value.toFixed(1)}
        {unit}
      </span>
    </div>
  );
}

function ExecutionRow({ exec }: { exec: SandboxExecution }) {
  const [expanded, setExpanded] = useState(false);
  const s = STATUS_MAP[exec.status] ?? STATUS_MAP.failed;

  return (
    <div className="border-b border-gray-100 last:border-0 dark:border-gray-800">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800/50"
        aria-expanded={expanded}
      >
        <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${s.color} ${s.bg}`}>
          {s.label}
        </span>
        <span className="flex-1 truncate font-medium">{exec.app_name}</span>
        <span className="text-xs text-gray-400">{formatDuration(exec.duration_ms)}</span>
        <span className="text-xs text-gray-400">{formatTime(exec.started_at)}</span>
        <span className="text-gray-400">{expanded ? "▾" : "▸"}</span>
      </button>

      {expanded && (
        <div className="space-y-2 bg-gray-50 px-4 py-3 dark:bg-gray-800/30">
          <div className="space-y-1">
            <ResourceBar label="CPU" value={exec.resources.cpu_seconds} max={30} unit="s" />
            <ResourceBar label="Wall" value={exec.resources.wall_seconds} max={120} unit="s" />
            <ResourceBar label="Memory" value={exec.resources.memory_mb} max={512} unit="MB" />
            <ResourceBar
              label="Network"
              value={exec.resources.network_egress_mb}
              max={10}
              unit="MB"
            />
          </div>

          {exec.exit_code !== null && (
            <p className="text-xs text-gray-500">
              Exit code:{" "}
              <code className={exec.exit_code === 0 ? "text-green-600" : "text-red-600"}>
                {exec.exit_code}
              </code>
            </p>
          )}

          {exec.error && (
            <p className="rounded bg-red-50 px-2 py-1 text-xs text-red-700 dark:bg-red-900/20 dark:text-red-400">
              {exec.error}
            </p>
          )}

          {exec.violations.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold uppercase text-red-600">Violations</p>
              <ul className="mt-0.5 space-y-0.5">
                {exec.violations.map((v, i) => (
                  <li key={i} className="text-xs text-red-600 dark:text-red-400">
                    • {v}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function SandboxExecutionLog({
  executions,
  totalCount,
  budgetUsed,
  budgetLimit,
}: SandboxExecutionLogProps) {
  const running = executions.filter((e) => e.status === "running").length;
  const failed = executions.filter((e) =>
    ["killed", "failed", "timeout"].includes(e.status),
  ).length;
  const budgetPct = budgetLimit > 0 ? Math.round((budgetUsed / budgetLimit) * 100) : 0;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">Sandbox Executions</h3>
            <p className="text-xs text-gray-500">
              {totalCount} total • {running} running • {failed} failed
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">Budget</p>
            <p
              className={`text-sm font-bold ${budgetPct > 90 ? "text-red-600" : budgetPct > 70 ? "text-yellow-600" : "text-green-600"}`}
            >
              {budgetUsed}/{budgetLimit}
            </p>
          </div>
        </div>
      </div>

      {executions.length === 0 ? (
        <div className="py-8 text-center">
          <span className="text-3xl">⚡</span>
          <p className="mt-2 text-sm text-gray-500">No sandbox executions yet</p>
        </div>
      ) : (
        <div>
          {executions.map((exec) => (
            <ExecutionRow key={exec.id} exec={exec} />
          ))}
        </div>
      )}
    </div>
  );
}
