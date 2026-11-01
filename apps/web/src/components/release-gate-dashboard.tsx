"use client";

interface GateCheck {
  name: string;
  status: "pending" | "passed" | "failed" | "skipped";
  required: boolean;
  message: string;
}

export function ReleaseGateDashboard({
  extensionName,
  version,
  checks,
  canRelease,
  onRelease,
  onRerun,
}: {
  extensionName: string;
  version: string;
  checks: GateCheck[];
  canRelease: boolean;
  onRelease?: () => void;
  onRerun?: (checkName: string) => void;
}) {
  const statusConfig: Record<string, { icon: string; color: string; bg: string }> = {
    pending: { icon: "⏳", color: "text-gray-500", bg: "bg-gray-100 dark:bg-gray-800" },
    passed: { icon: "✅", color: "text-green-500", bg: "bg-green-50 dark:bg-green-900/10" },
    failed: { icon: "❌", color: "text-red-500", bg: "bg-red-50 dark:bg-red-900/10" },
    skipped: { icon: "⏭️", color: "text-gray-400", bg: "bg-gray-50 dark:bg-gray-800" },
  };

  const passed = checks.filter((c) => c.status === "passed").length;
  const failed = checks.filter((c) => c.status === "failed").length;
  const pending = checks.filter((c) => c.status === "pending").length;

  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 space-y-4 max-w-lg">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold">🚦 Release Gate</h2>
          <p className="text-sm text-gray-500">{extensionName} v{version}</p>
        </div>
        <div className={`text-sm font-bold px-3 py-1 rounded-full ${
          canRelease ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
          : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
        }`}>
          {canRelease ? "Ready" : "Blocked"}
        </div>
      </div>

      <div className="flex gap-3 text-xs">
        <span className="text-green-500">✅ {passed} passed</span>
        <span className="text-red-500">❌ {failed} failed</span>
        <span className="text-gray-400">⏳ {pending} pending</span>
      </div>

      <div className="space-y-2">
        {checks.map((check) => {
          const cfg = statusConfig[check.status];
          return (
            <div key={check.name} className={`flex items-center justify-between rounded-lg p-3 ${cfg.bg}`}>
              <div className="flex items-center gap-2">
                <span>{cfg.icon}</span>
                <div>
                  <div className="text-sm font-medium">{check.name}</div>
                  {check.message && <div className="text-xs text-gray-400">{check.message}</div>}
                </div>
                {!check.required && <span className="text-xs text-gray-400">(optional)</span>}
              </div>
              {check.status === "failed" && onRerun && (
                <button onClick={() => onRerun(check.name)}
                  className="text-xs text-blue-500 border border-blue-300 dark:border-blue-700 px-2 py-0.5 rounded">
                  🔄 Rerun
                </button>
              )}
            </div>
          );
        })}
      </div>

      <button onClick={onRelease} disabled={!canRelease}
        className="w-full rounded-lg bg-green-600 text-white py-2.5 text-sm font-bold disabled:opacity-50">
        {canRelease ? "🚀 Release v" + version : "🔒 Release Blocked"}
      </button>
    </div>
  );
}
