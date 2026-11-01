"use client";
interface DataRedactPanelProps { redactedFields: number; patternsActive: number; samplesProcessed: number; }
export function DataRedactPanel({ redactedFields, patternsActive, samplesProcessed }: DataRedactPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Data Redaction</h3>
        <span className="text-xs text-gray-400">{patternsActive} patterns · {samplesProcessed.toLocaleString()} processed</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Redacted</span><div className="font-bold text-lg text-red-500">{redactedFields.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Patterns</span><div className="font-bold text-lg">{patternsActive}</div></div>
        <div><span className="text-gray-400">Processed</span><div className="font-bold text-lg">{samplesProcessed.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
