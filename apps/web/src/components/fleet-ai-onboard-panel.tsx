"use client";
export function FleetAiOnboardPanel({ wizards, active, completions, avgMin, dropOff }: { wizards: number; active: number; completions: number; avgMin: number; dropOff: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Onboarding</h3>
    <div className="text-sm">{active}/{wizards} active · {completions.toLocaleString()} completions · {avgMin}m avg · {dropOff}% drop-off</div>
  </div>);
}
