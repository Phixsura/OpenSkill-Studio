"use client";
export function FleetAiApiVerPanel({ versioners, active, apis, versions, deprecated }: { versioners: number; active: number; apis: number; versions: number; deprecated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI API Versioner</h3>
    <div className="text-sm">{active}/{versioners} active · {apis} APIs · {versions} versions · {deprecated} deprecated</div>
  </div>);
}
