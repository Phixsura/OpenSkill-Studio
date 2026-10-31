"use client";
export function FleetAiModelDeprPanel({ managers, active, deprecated, migrated, sunsetDays }: { managers: number; active: number; deprecated: number; migrated: number; sunsetDays: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏳ AI Model Deprecation</h3>
    <div className="text-sm">{active}/{managers} active · {deprecated} deprecated · {migrated} migrated · sunset in {sunsetDays}d</div>
  </div>);
}
