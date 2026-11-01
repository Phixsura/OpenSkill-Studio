"use client";
export function FleetAiFeatFlagPanel({ systems, active, flags, enabled, evaluations }: { systems: number; active: number; flags: number; enabled: number; evaluations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚩 AI Feature Flags</h3>
    <div className="text-sm">{active}/{systems} active · {enabled}/{flags} enabled · {evaluations.toLocaleString()} evals</div>
  </div>);
}
