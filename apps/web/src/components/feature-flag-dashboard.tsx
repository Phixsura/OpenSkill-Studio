"use client";

import { useState } from "react";

interface FlagRule {
  rule_type: "boolean" | "percentage" | "user_list" | "tenant_list";
  value: boolean | number | string[];
}

interface FeatureFlag {
  key: string;
  description: string;
  status: "active" | "disabled" | "archived";
  default_value: boolean;
  rules: FlagRule[];
  depends_on: string[];
}

interface FlagEvalResult {
  key: string;
  enabled: boolean;
  reason: string;
}

interface FeatureFlagDashboardProps {
  flags: FeatureFlag[];
  evaluations: Record<string, FlagEvalResult>;
  onToggle: (key: string, enabled: boolean) => void;
  onArchive: (key: string) => void;
}

const STATUS_STYLES: Record<string, { dot: string; label: string }> = {
  active: { dot: "bg-green-500", label: "Active" },
  disabled: { dot: "bg-gray-400", label: "Disabled" },
  archived: { dot: "bg-red-400", label: "Archived" },
};

function ruleLabel(rule: FlagRule): string {
  switch (rule.rule_type) {
    case "boolean":
      return rule.value ? "On" : "Off";
    case "percentage":
      return `${rule.value}% rollout`;
    case "user_list":
      return `${Array.isArray(rule.value) ? rule.value.length : 0} users`;
    case "tenant_list":
      return `${Array.isArray(rule.value) ? rule.value.length : 0} tenants`;
    default:
      return rule.rule_type;
  }
}

function FlagRow({
  flag,
  evaluation,
  onToggle,
  onArchive,
}: {
  flag: FeatureFlag;
  evaluation: FlagEvalResult | undefined;
  onToggle: (key: string, enabled: boolean) => void;
  onArchive: (key: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const st = STATUS_STYLES[flag.status] ?? STATUS_STYLES.disabled;
  const isOn = evaluation?.enabled ?? flag.default_value;

  return (
    <div className="border-b border-gray-100 last:border-0 dark:border-gray-800">
      <div className="flex items-center gap-3 px-4 py-3">
        {/* Toggle */}
        <button
          onClick={() => onToggle(flag.key, !isOn)}
          className={`relative h-5 w-9 rounded-full transition-colors ${isOn ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}
          role="switch"
          aria-checked={isOn}
          aria-label={`Toggle ${flag.key}`}
        >
          <span
            className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${isOn ? "left-[18px]" : "left-0.5"}`}
          />
        </button>

        {/* Info */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex flex-1 items-center gap-2 text-left"
        >
          <span className={`h-2 w-2 rounded-full ${st.dot}`} />
          <div className="flex-1">
            <span className="text-sm font-medium">{flag.key}</span>
            <span className="ml-2 text-xs text-gray-400">{flag.description}</span>
          </div>
          {flag.rules.length > 0 && (
            <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800">
              {flag.rules.map(ruleLabel).join(", ")}
            </span>
          )}
          <span className="text-gray-400">{expanded ? "▾" : "▸"}</span>
        </button>
      </div>

      {expanded && (
        <div className="space-y-2 bg-gray-50 px-4 pb-3 dark:bg-gray-800/30">
          <div className="flex gap-4 text-xs text-gray-500">
            <span>Status: {st.label}</span>
            <span>Default: {flag.default_value ? "on" : "off"}</span>
            {evaluation && <span>Eval: {evaluation.reason}</span>}
          </div>

          {flag.rules.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold uppercase text-gray-400">Rules</p>
              <ul className="mt-1 space-y-1">
                {flag.rules.map((r, i) => (
                  <li key={i} className="text-xs">
                    Rule {i}: <code>{r.rule_type}</code> = <code>{JSON.stringify(r.value)}</code>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {flag.depends_on.length > 0 && (
            <p className="text-xs text-gray-500">
              Depends on:{" "}
              {flag.depends_on.map((d) => (
                <code key={d} className="mr-1">
                  {d}
                </code>
              ))}
            </p>
          )}

          {flag.status !== "archived" && (
            <button
              onClick={() => onArchive(flag.key)}
              className="rounded border border-red-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400"
            >
              Archive
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export function FeatureFlagDashboard({
  flags,
  evaluations,
  onToggle,
  onArchive,
}: FeatureFlagDashboardProps) {
  const [filter, setFilter] = useState<"all" | "active" | "disabled" | "archived">("all");
  const filtered = filter === "all" ? flags : flags.filter((f) => f.status === filter);
  const active = flags.filter((f) => f.status === "active").length;
  const disabled = flags.filter((f) => f.status === "disabled").length;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">Feature Flags</h3>
            <p className="text-xs text-gray-500">
              {flags.length} flags • {active} active • {disabled} disabled
            </p>
          </div>
          <div className="flex gap-1">
            {(["all", "active", "disabled", "archived"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`rounded px-2 py-1 text-xs ${filter === f ? "bg-blue-600 text-white" : "text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"}`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="py-8 text-center text-sm text-gray-500">No flags match filter</div>
      ) : (
        <div>
          {filtered.map((flag) => (
            <FlagRow
              key={flag.key}
              flag={flag}
              evaluation={evaluations[flag.key]}
              onToggle={onToggle}
              onArchive={onArchive}
            />
          ))}
        </div>
      )}
    </div>
  );
}
