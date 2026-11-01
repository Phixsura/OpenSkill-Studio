"use client";

interface ScopeAnalysis {
  app_id: string;
  declared_scopes: string[];
  exercised_scopes: string[];
  unused_scopes: string[];
  undeclared_attempts: string[];
  compliance_pct: number;
  over_permissioned: boolean;
  under_permissioned: boolean;
  recommendations: string[];
}

interface ScopeAnalysisCardProps {
  analysis: ScopeAnalysis;
  appName: string;
}

function ComplianceRing({ pct }: { pct: number }) {
  const r = 32;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;
  const color = pct >= 90 ? "stroke-green-500" : pct >= 60 ? "stroke-yellow-500" : "stroke-red-500";
  const textColor = pct >= 90 ? "text-green-600" : pct >= 60 ? "text-yellow-600" : "text-red-600";
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="72" height="72" className="-rotate-90">
        <circle
          cx="36"
          cy="36"
          r={r}
          fill="none"
          strokeWidth="5"
          className="stroke-gray-200 dark:stroke-gray-700"
        />
        <circle
          cx="36"
          cy="36"
          r={r}
          fill="none"
          strokeWidth="5"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={color}
        />
      </svg>
      <span className={`absolute text-sm font-bold ${textColor}`}>{pct}%</span>
    </div>
  );
}

function ScopeChipGroup({
  label,
  scopes,
  color,
}: {
  label: string;
  scopes: string[];
  color: string;
}) {
  if (scopes.length === 0) return null;
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase text-gray-400">
        {label} ({scopes.length})
      </p>
      <div className="mt-1 flex flex-wrap gap-1">
        {scopes.map((s) => (
          <code key={s} className={`rounded px-1.5 py-0.5 text-[10px] ${color}`}>
            {s}
          </code>
        ))}
      </div>
    </div>
  );
}

export function ScopeAnalysisCard({ analysis, appName }: ScopeAnalysisCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">Scope Analysis</h3>
          <p className="text-xs text-gray-500">
            {appName} • {analysis.declared_scopes.length} declared
          </p>
        </div>
        <ComplianceRing pct={analysis.compliance_pct} />
      </div>

      {/* Status flags */}
      <div className="flex gap-2 border-b border-gray-200 px-4 py-2 dark:border-gray-700">
        {analysis.over_permissioned && (
          <span className="rounded bg-yellow-100 px-2 py-0.5 text-[10px] font-medium text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300">
            Over-permissioned
          </span>
        )}
        {analysis.under_permissioned && (
          <span className="rounded bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/20 dark:text-red-300">
            Under-permissioned
          </span>
        )}
        {!analysis.over_permissioned && !analysis.under_permissioned && (
          <span className="rounded bg-green-100 px-2 py-0.5 text-[10px] font-medium text-green-700 dark:bg-green-900/20 dark:text-green-300">
            ✓ Correctly scoped
          </span>
        )}
      </div>

      {/* Scope groups */}
      <div className="space-y-3 px-4 py-3">
        <ScopeChipGroup
          label="Exercised"
          scopes={analysis.exercised_scopes}
          color="bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300"
        />
        <ScopeChipGroup
          label="Unused"
          scopes={analysis.unused_scopes}
          color="bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300"
        />
        <ScopeChipGroup
          label="Denied Attempts"
          scopes={analysis.undeclared_attempts}
          color="bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"
        />
      </div>

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div className="border-t border-gray-200 px-4 py-2 dark:border-gray-700">
          <p className="text-[10px] font-semibold uppercase text-gray-400">Recommendations</p>
          <ul className="mt-1 space-y-0.5">
            {analysis.recommendations.map((r, i) => (
              <li key={i} className="text-xs text-gray-600 dark:text-gray-400">
                💡 {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
