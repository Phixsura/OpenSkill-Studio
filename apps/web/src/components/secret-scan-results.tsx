"use client";

interface Finding { type: string; severity: string; line: number; file: string; matchPreview: string; }
interface SecretScanResultsProps { totalFiles: number; totalFindings: number;
  findings: Finding[]; clean: boolean; }

const SEV_STYLE: Record<string, string> = {
  critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", medium: "bg-yellow-100 text-yellow-700",
};

export function SecretScanResults({ totalFiles, totalFindings, findings, clean }: SecretScanResultsProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔍 Secret Scanner</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${clean ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {clean ? "✅ Clean" : `⚠️ ${totalFindings} secrets found`}
        </span>
      </div>
      <p className="text-xs text-gray-400 mb-3">{totalFiles} files scanned</p>
      {findings.length > 0 && (
        <div className="space-y-2">
          {findings.map((f, i) => (
            <div key={i} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm">
              <div>
                <span className={`text-xs px-1.5 py-0.5 rounded mr-2 ${SEV_STYLE[f.severity] || ""}`}>{f.severity}</span>
                <span className="font-mono text-xs">{f.file}:{f.line}</span>
              </div>
              <span className="text-xs text-gray-400">{f.type}: {f.matchPreview}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
