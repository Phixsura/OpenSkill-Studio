"use client";

interface Permission {
  scope: string;
  risk: "low" | "medium" | "high" | "critical";
  category: string;
  description: string;
  requires_review: boolean;
}

interface ScanResult {
  permissions: Permission[];
  total_scopes: number;
  trust_score: number;
  warnings: string[];
  requires_human_review: boolean;
  human_summary: string;
}

interface AppPermissionReviewProps {
  appName: string;
  scanResult: ScanResult;
  onApprove: () => void;
  onReject: () => void;
}

const RISK_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  low: {
    label: "Low",
    color: "text-green-700 dark:text-green-300",
    bg: "bg-green-100 dark:bg-green-900/30",
  },
  medium: {
    label: "Medium",
    color: "text-yellow-700 dark:text-yellow-300",
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
  },
  high: {
    label: "High",
    color: "text-orange-700 dark:text-orange-300",
    bg: "bg-orange-100 dark:bg-orange-900/30",
  },
  critical: {
    label: "Critical",
    color: "text-red-700 dark:text-red-300",
    bg: "bg-red-100 dark:bg-red-900/30",
  },
};

function RiskBadge({ risk }: { risk: string }) {
  const config = RISK_CONFIG[risk] ?? RISK_CONFIG.high;
  return (
    <span
      className={`rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase ${config.color} ${config.bg}`}
    >
      {config.label}
    </span>
  );
}

function TrustScoreRing({ score }: { score: number }) {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? "text-green-500" : score >= 50 ? "text-yellow-500" : "text-red-500";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="88" height="88" className="-rotate-90">
        <circle
          cx="44"
          cy="44"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          className="text-gray-200 dark:text-gray-700"
        />
        <circle
          cx="44"
          cy="44"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={color}
        />
      </svg>
      <span className="absolute text-lg font-bold">{score}</span>
    </div>
  );
}

export function AppPermissionReview({
  appName,
  scanResult,
  onApprove,
  onReject,
}: AppPermissionReviewProps) {
  const { permissions, trust_score, warnings, requires_human_review, human_summary } = scanResult;

  const grouped = permissions.reduce<Record<string, Permission[]>>((acc, p) => {
    (acc[p.category] ??= []).push(p);
    return acc;
  }, {});

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Permission Review</h2>
            <p className="text-sm text-gray-500">
              <span className="font-medium">{appName}</span> requests {scanResult.total_scopes}{" "}
              permission{scanResult.total_scopes !== 1 ? "s" : ""}
            </p>
          </div>
          <TrustScoreRing score={trust_score} />
        </div>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{human_summary}</p>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="border-b border-gray-200 bg-yellow-50 px-4 py-3 dark:border-gray-700 dark:bg-yellow-900/10">
          <p className="text-xs font-semibold text-yellow-800 dark:text-yellow-300">⚠ Warnings</p>
          <ul className="mt-1 space-y-1">
            {warnings.map((w, i) => (
              <li key={i} className="text-xs text-yellow-700 dark:text-yellow-400">
                • {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Permissions by category */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {Object.entries(grouped).map(([category, perms]) => (
          <div key={category} className="px-4 py-3">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-400">
              {category}
            </h4>
            <ul className="mt-2 space-y-2">
              {perms.map((p) => (
                <li key={p.scope} className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <code className="text-xs font-medium">{p.scope}</code>
                      <RiskBadge risk={p.risk} />
                      {p.requires_review && (
                        <span className="text-[10px] text-red-500">requires review</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">{p.description}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3 dark:border-gray-700">
        {requires_human_review && (
          <span className="text-xs font-medium text-red-600 dark:text-red-400">
            🔒 Requires human review before publishing
          </span>
        )}
        {!requires_human_review && <span />}
        <div className="flex gap-2">
          <button
            onClick={onReject}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
          >
            Reject
          </button>
          <button
            onClick={onApprove}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}
