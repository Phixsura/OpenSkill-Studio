"use client";

interface AuditResult {
  extensionId: string; totalPermissions: number; usedPermissions: number;
  unusedPermissions: string[]; dangerousCombos: string[];
  riskScore: number; escalations: string[]; recommendation: string;
}

function riskColor(score: number) {
  if (score <= 5) return "text-green-600";
  if (score <= 15) return "text-yellow-600";
  return "text-red-600";
}

export function PermissionAuditReport({ result }: { result: AuditResult }) {
  const usagePct = result.totalPermissions > 0
    ? Math.round(result.usedPermissions / result.totalPermissions * 100) : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm">Permission Audit</h3>
        <span className={`text-sm font-bold ${riskColor(result.riskScore)}`}>
          Risk Score: {result.riskScore}
        </span>
      </div>

      {/* Usage meter */}
      <div className="border dark:border-gray-700 rounded-xl p-3">
        <div className="flex justify-between text-xs mb-1">
          <span>Permission Usage</span>
          <span>{result.usedPermissions}/{result.totalPermissions} used ({usagePct}%)</span>
        </div>
        <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden flex">
          <div className="h-full bg-green-500" style={{ width: `${usagePct}%` }} />
          <div className="h-full bg-red-300" style={{ width: `${100 - usagePct}%` }} />
        </div>
        <div className="flex gap-4 mt-1 text-[10px] text-gray-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-green-500" /> Active</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-red-300" /> Unused</span>
        </div>
      </div>

      {/* Recommendation */}
      <div className={`rounded-xl p-3 text-sm ${
        result.recommendation.startsWith("✅") ? "bg-green-50 dark:bg-green-900/10" :
        result.recommendation.startsWith("🔴") ? "bg-red-50 dark:bg-red-900/10" :
        "bg-yellow-50 dark:bg-yellow-900/10"
      }`}>{result.recommendation}</div>

      {/* Dangerous combos */}
      {result.dangerousCombos.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-red-600 mb-1">🔴 Dangerous Combinations</h4>
          {result.dangerousCombos.map((c, i) => (
            <div key={i} className="text-xs bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg p-2 mb-1">{c}</div>
          ))}
        </div>
      )}

      {/* Escalations */}
      {result.escalations.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-orange-600 mb-1">⬆️ Permission Escalations</h4>
          {result.escalations.map((e, i) => (
            <div key={i} className="text-xs text-orange-600 ml-2">• {e}</div>
          ))}
        </div>
      )}

      {/* Unused permissions */}
      {result.unusedPermissions.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 mb-1">Unused Permissions</h4>
          {result.unusedPermissions.map((p, i) => (
            <div key={i} className="text-xs text-gray-400 ml-2">• {p}</div>
          ))}
        </div>
      )}
    </div>
  );
}
