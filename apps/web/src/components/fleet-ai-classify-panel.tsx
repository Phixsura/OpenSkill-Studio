"use client";
export function FleetAiClassifyPanel({ services, active, classifications, accuracy }: { services: number; active: number; classifications: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI Classification</h3>
    <div className="text-sm">{active}/{services} active · {classifications.toLocaleString()} classified · {accuracy}% accuracy</div>
  </div>);
}
