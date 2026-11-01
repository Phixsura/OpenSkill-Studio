"use client";
export function FleetOnboardingV9Panel({ total, avgDays }: { total: number; avgDays: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎓 Onboarding v9</h3>
    <div className="text-sm">{total} devs · {avgDays}d avg to productive</div>
  </div>);
}
