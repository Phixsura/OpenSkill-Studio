"use client";

interface PayloadInspectorProps { formatted: string; sizeDisplay: string;
  depth: number; fieldCount: number; fields: string[]; warnings: string[]; }

export function PayloadInspector({ formatted, sizeDisplay, depth, fieldCount, fields, warnings }: PayloadInspectorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-3 border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <h3 className="text-sm font-semibold">🔎 Payload Inspector</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{sizeDisplay}</span>
          <span>Depth: {depth}</span>
          <span>{fieldCount} fields</span>
        </div>
      </div>
      {warnings.length > 0 && (
        <div className="px-3 py-2 bg-yellow-50 dark:bg-yellow-900/20 text-xs text-yellow-700">
          {warnings.map((w, i) => <p key={i}>⚠️ {w}</p>)}
        </div>
      )}
      <div className="flex gap-2 px-3 py-2 text-xs flex-wrap border-b dark:border-gray-700">
        {fields.map(f => <span key={f} className="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/20 text-blue-700 rounded">{f}</span>)}
      </div>
      <pre className="p-3 text-xs font-mono bg-gray-900 text-green-400 overflow-auto max-h-64">{formatted}</pre>
    </div>
  );
}
