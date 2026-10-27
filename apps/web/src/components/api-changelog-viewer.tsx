"use client";

import { useState } from "react";

interface ParamChange {
  name: string;
  change_type: "added" | "removed" | "modified";
  old_type: string | null;
  new_type: string | null;
}

interface Change {
  method: string;
  path: string;
  change_type: "added" | "removed" | "modified" | "deprecated";
  severity: "breaking" | "non_breaking" | "patch";
  summary: string;
  param_changes: ParamChange[];
  response_changes: ParamChange[];
  migration_hint: string | null;
}

interface ChangelogData {
  from_version: string;
  to_version: string;
  generated_at: string;
  summary: {
    breaking: number;
    non_breaking: number;
    patch: number;
    has_breaking: boolean;
  };
  changes: Change[];
}

interface ApiChangelogViewerProps {
  changelog: ChangelogData;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  POST: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  PATCH: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
  PUT: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
};

const CHANGE_ICONS: Record<string, { icon: string; color: string }> = {
  added: { icon: "+", color: "text-green-600 dark:text-green-400" },
  removed: { icon: "−", color: "text-red-600 dark:text-red-400" },
  modified: { icon: "~", color: "text-yellow-600 dark:text-yellow-400" },
  deprecated: { icon: "⚠", color: "text-orange-600 dark:text-orange-400" },
};

function MethodBadge({ method }: { method: string }) {
  const color = METHOD_COLORS[method] ?? METHOD_COLORS.GET;
  return (
    <span
      className={`inline-block w-16 rounded px-1.5 py-0.5 text-center text-[10px] font-bold ${color}`}
    >
      {method}
    </span>
  );
}

function SeverityDot({ severity }: { severity: string }) {
  const color =
    severity === "breaking"
      ? "bg-red-500"
      : severity === "non_breaking"
        ? "bg-green-500"
        : "bg-gray-400";
  return <span className={`inline-block h-2 w-2 rounded-full ${color}`} />;
}

function ChangeRow({ change }: { change: Change }) {
  const [expanded, setExpanded] = useState(false);
  const ci = CHANGE_ICONS[change.change_type] ?? CHANGE_ICONS.modified;
  const hasDetails =
    change.param_changes.length > 0 || change.response_changes.length > 0 || change.migration_hint;

  return (
    <div className="border-b border-gray-100 last:border-0 dark:border-gray-800">
      <button
        onClick={() => hasDetails && setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800/50"
        aria-expanded={hasDetails ? expanded : undefined}
      >
        <SeverityDot severity={change.severity} />
        <span className={`font-mono text-base ${ci.color}`}>{ci.icon}</span>
        <MethodBadge method={change.method} />
        <code className="flex-1 truncate text-xs">{change.path}</code>
        {hasDetails && <span className="text-gray-400">{expanded ? "▾" : "▸"}</span>}
      </button>

      {expanded && hasDetails && (
        <div className="space-y-2 bg-gray-50 px-4 py-3 dark:bg-gray-800/30">
          <p className="text-xs text-gray-600 dark:text-gray-400">{change.summary}</p>

          {change.param_changes.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold uppercase text-gray-400">Parameters</p>
              <ul className="mt-1 space-y-0.5">
                {change.param_changes.map((p) => (
                  <li key={p.name} className="flex items-center gap-2 text-xs">
                    <span className={CHANGE_ICONS[p.change_type]?.color ?? ""}>
                      {CHANGE_ICONS[p.change_type]?.icon}
                    </span>
                    <code>{p.name}</code>
                    {p.old_type && p.new_type && (
                      <span className="text-gray-400">
                        {p.old_type} → {p.new_type}
                      </span>
                    )}
                    {p.new_type && !p.old_type && (
                      <span className="text-gray-400">{p.new_type}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {change.response_changes.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold uppercase text-gray-400">Response</p>
              <ul className="mt-1 space-y-0.5">
                {change.response_changes.map((r) => (
                  <li key={r.name} className="flex items-center gap-2 text-xs">
                    <span className={CHANGE_ICONS[r.change_type]?.color ?? ""}>
                      {CHANGE_ICONS[r.change_type]?.icon}
                    </span>
                    <code>{r.name}</code>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {change.migration_hint && (
            <div className="rounded bg-blue-50 px-2 py-1.5 text-xs text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">
              💡 <strong>Migration:</strong> {change.migration_hint}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ApiChangelogViewer({ changelog }: ApiChangelogViewerProps) {
  const { summary, changes } = changelog;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <h3 className="font-semibold">
          API Changelog: {changelog.from_version} → {changelog.to_version}
        </h3>
        <div className="mt-1 flex gap-3 text-xs">
          {summary.breaking > 0 && (
            <span className="font-medium text-red-600">🔴 {summary.breaking} breaking</span>
          )}
          {summary.non_breaking > 0 && (
            <span className="text-green-600">🟢 {summary.non_breaking} non-breaking</span>
          )}
          {summary.patch > 0 && <span className="text-gray-500">{summary.patch} patch</span>}
        </div>
      </div>

      {/* Breaking warning */}
      {summary.has_breaking && (
        <div className="bg-red-50 px-4 py-2 text-xs font-medium text-red-700 dark:bg-red-900/10 dark:text-red-400">
          ⚠️ This version contains breaking changes. Review migration hints before upgrading.
        </div>
      )}

      {/* Changes */}
      {changes.length === 0 ? (
        <div className="py-8 text-center text-sm text-gray-500">No changes detected</div>
      ) : (
        <div>
          {changes.map((c, i) => (
            <ChangeRow key={`${c.method}-${c.path}-${i}`} change={c} />
          ))}
        </div>
      )}
    </div>
  );
}
