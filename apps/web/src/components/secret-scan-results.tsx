"use client";

interface Finding { type: string; severity: string; preview: string; filename: string; }
interface SecretScanResultsProps { findings: Finding[]; clean: boolean; onRevoke: (preview: string) => void; }

const sevBadge: Record<string, string> = {
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
};

export function SecretScanResults({ findings, clean, onRevoke }: SecretScanResultsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Secret Scan</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${clean ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {clean ? "✅ Clean" : `🚨 ${findings.length} secrets found`}
        </span>
      </div>
      {findings.map((f, i) => (
        <div key={i} className="flex items-center justify-between rounded-lg border border-red-200 p-3 dark:border-red-800">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{f.type}</span>
              <span className={`rounded-full px-1.5 py-0.5 text-[10px] ${sevBadge[f.severity] ?? ""}`}>{f.severity}</span>
            </div>
            <p className="mt-0.5 font-mono text-xs text-gray-400">{f.preview} · {f.filename}</p>
          </div>
          <button onClick={() => onRevoke(f.preview)} className="rounded bg-red-600 px-2 py-1 text-xs text-white">Revoke</button>
        </div>
      ))}
      {clean && <p className="text-center text-sm text-green-600">No secrets detected in your code ✓</p>}
    </div>
  );
}
