"use client";
export function FleetOnboardingPanel({ total, onboarded, pending, avgDays, fast }: { total: number; onboarded: number; pending: number; avgDays: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👋 Developer Onboarding</h3>
    <div className="text-sm">{onboarded}/{total} onboarded · avg {avgDays} days</div>
    {pending > 0 && <span className="text-xs text-blue-500">{pending} pending</span>}
  </div>);
}
