"use client";

interface CspBuilderPanelProps { header: string; directives: Record<string, string[]>;
  warnings: string[]; directiveCount: number; }

export function CspBuilderPanel({ header, directives, warnings, directiveCount }: CspBuilderPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Content Security Policy</h3>
        <span className="text-xs text-gray-400">{directiveCount} directives</span>
      </div>
      <pre className="overflow-x-auto rounded-lg bg-gray-950 p-3 text-xs text-green-400 font-mono">{header}</pre>
      {warnings.length > 0 && (
        <div className="space-y-1">
          {warnings.map((w, i) => (
            <p key={i} className="text-xs text-yellow-600 flex items-center gap-1">
              <span>⚠</span>{w}
            </p>
          ))}
        </div>
      )}
      <div className="space-y-1">
        {Object.entries(directives).map(([k, v]) => (
          <div key={k} className="flex items-start gap-2 text-xs">
            <span className="font-mono font-medium w-32 shrink-0">{k}</span>
            <span className="text-gray-500">{v.join(" ")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
