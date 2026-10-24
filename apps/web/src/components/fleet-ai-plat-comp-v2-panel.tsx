"use client";
export function FleetAiPlatCompV2Panel({ frameworks, active, certifications, controls, compliance }: { frameworks: number; active: number; certifications: string[]; controls: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Compliance v2</h3>
    <div className="text-sm">{active}/{frameworks} active · {certifications.join(", ")} · {controls} controls · {compliance}%</div>
  </div>);
}
