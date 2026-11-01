"use client";

interface StatCard { key: string; label: string; value: string | number; icon: string; url?: string; }
interface QuickAction { label: string; url: string; icon: string; primary?: boolean; }
interface DeveloperHomepageLayoutProps {
  name: string; plan: string; verified: boolean;
  statsCards: StatCard[]; quickActions: QuickAction[];
  hasOnboarding: boolean; onboardingPct?: number;
}

export function DeveloperHomepageLayout({ name, plan, verified, statsCards, quickActions, hasOnboarding, onboardingPct }: DeveloperHomepageLayoutProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Welcome back, {name}! {verified && "✅"}</h1>
          <p className="text-sm text-gray-400">Plan: {plan}</p>
        </div>
        <div className="flex gap-2">
          {quickActions.map(a => (
            <a key={a.label} href={a.url}
              className={`rounded-lg px-4 py-2 text-sm ${a.primary ? "bg-blue-600 text-white" : "border border-gray-200 dark:border-gray-700"}`}>
              {a.icon} {a.label}
            </a>
          ))}
        </div>
      </div>
      {hasOnboarding && (
        <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
          <p className="text-sm font-medium">Getting Started — {onboardingPct}% complete</p>
          <div className="mt-1 h-2 rounded-full bg-blue-200 dark:bg-blue-800">
            <div className="h-full rounded-full bg-blue-600" style={{ width: `${onboardingPct}%` }} />
          </div>
        </div>
      )}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {statsCards.map(s => (
          <div key={s.key} className="rounded-lg border border-gray-200 p-4 text-center dark:border-gray-700">
            <span className="text-xl">{s.icon}</span>
            <p className="mt-1 text-2xl font-bold">{typeof s.value === "number" ? s.value.toLocaleString() : s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
