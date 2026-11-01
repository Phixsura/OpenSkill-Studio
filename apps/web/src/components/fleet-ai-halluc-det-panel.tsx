"use client";
export function FleetAiHallucDetPanel({ detectors, active, checked, hallucinations, detectionRate }: { detectors: number; active: number; checked: number; hallucinations: number; detectionRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Hallucination Detector</h3>
    <div className="text-sm">{active}/{detectors} active · {checked.toLocaleString()} checked · {hallucinations.toLocaleString()} caught · {detectionRate}% rate</div>
  </div>);
}
