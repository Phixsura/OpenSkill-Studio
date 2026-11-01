"use client";
export function FleetAiExtractPanel({ services, active, docs, entities }: { services: number; active: number; docs: number; entities: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Extraction</h3>
    <div className="text-sm">{active}/{services} active · {docs.toLocaleString()} docs · {entities.toLocaleString()} entities</div>
  </div>);
}
