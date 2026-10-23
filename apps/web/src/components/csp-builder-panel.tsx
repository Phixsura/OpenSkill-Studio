"use client";

interface CspBuilderPanelProps { headerValue: string; directives: Record<string, string[]>;
  securityScore: number; warnings: string[]; onUpdate: (directives: Record<string, string[]>) => void; }

export function CspBuilderPanel({ headerValue, directives, securityScore, warnings, onUpdate }: CspBuilderPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Content Security Policy</h2>
        <span className={`text-lg font-bold ${securityScore >= 80 ? "text-green-600" : securityScore >= 50 ? "text-yellow-600" : "text-red-600"}`}>
          {securityScore}/100
        </span>
      </div>
      <div className="rounded bg-gray-900 p-3 font-mono text-xs text-green-400">
        <p className="break-all">{headerValue}</p>
      </div>
      {warnings.length > 0 && (
        <div className="space-y-1">
          {warnings.map((w, i) => (
            <p key={i} className="text-xs text-yellow-600">⚠️ {w}</p>
          ))}
        </div>
      )}
      <div className="space-y-2">
        {Object.entries(directives).map(([dir, sources]) => (
          <div key={dir} className="flex items-center gap-2 rounded border px-3 py-1.5 dark:border-gray-700">
            <span className="w-32 font-mono text-xs font-bold text-blue-500">{dir}</span>
            <span className="flex-1 font-mono text-xs text-gray-400">{sources.join(" ")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
