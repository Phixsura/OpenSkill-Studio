"use client";
export function FleetAiPromptDefPanel({ defenders, active, scanned, blocked, fpRate }: { defenders: number; active: number; scanned: number; blocked: number; fpRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Prompt Defense</h3>
    <div className="text-sm">{active}/{defenders} active · {scanned.toLocaleString()} scanned · {blocked} blocked · {fpRate}% FP</div>
  </div>);
}
