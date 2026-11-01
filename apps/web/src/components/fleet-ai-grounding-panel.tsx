"use client";
export function FleetAiGroundingPanel({ engines, active, responses, grounded, sources }: { engines: number; active: number; responses: number; grounded: number; sources: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚓ AI Grounding Engine</h3>
    <div className="text-sm">{active}/{engines} active · {responses.toLocaleString()} resp · {grounded}% grounded · {sources.toLocaleString()} sources</div>
  </div>);
}
