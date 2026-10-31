"use client";
export function FleetApiDeveloperOnboardingV9Panel({ devs, onboarded }: { devs: number; onboarded: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎓 Dev Onboarding v9</h3>
    <div className="text-sm">{devs} devs · {onboarded} onboarded</div>
  </div>);
}
