"use client";
interface Enrichment { field: string; source: string; }
interface ReqEnrichPanelProps { enrichments: Enrichment[]; totalFields: number; applied: number; }
export function ReqEnrichPanel({ enrichments, totalFields, applied }: ReqEnrichPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✨ Request Enrichment</h3>
        <span className="text-xs text-gray-400">{applied} enriched · {totalFields} total fields</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {enrichments.map(e => (
          <div key={e.field} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono text-green-600">+ {e.field}</span>
            <span className="text-gray-400">from {e.source}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
