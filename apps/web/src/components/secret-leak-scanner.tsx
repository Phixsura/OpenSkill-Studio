"use client";

interface Finding { type: string; severity: string; file: string; matchPreview: string; }
interface SecretLeakScannerProps { findings: Finding[]; filesScanned: number;
  cleanFiles: number; totalFindings: number; pass: boolean; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", high: "bg-orange-500 text-white", medium: "bg-yellow-400",
};

export function SecretLeakScanner({ findings, filesScanned, cleanFiles, totalFindings, pass }: SecretLeakScannerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${pass ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold">🔐 Secret Scanner</h3>
        <span className={`text-xs ${pass ? "text-green-600" : "text-red-500"}`}>
          {pass ? "✅ Clean" : `⚠ ${totalFindings} secrets found`} · {filesScanned} files
        </span>
      </div>
      {findings.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {findings.map((f, i) => (
            <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
              <div className="flex gap-2">
                <span className={`px-1 py-0.5 text-[10px] rounded ${SEV_COLORS[f.severity] ?? ""}`}>{f.severity}</span>
                <span>{f.type}</span>
              </div>
              <span className="text-gray-400 font-mono">{f.file}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
