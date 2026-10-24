"use client";

interface NextStep { label: string; href: string; icon: string; primary?: boolean; }
interface OnboardingCompletePageProps { headline: string; subtitle: string;
  planLabel: string; nextSteps: NextStep[]; onNavigate: (href: string) => void; }

export function OnboardingCompletePage({ headline, subtitle, planLabel, nextSteps, onNavigate }: OnboardingCompletePageProps) {
  return (
    <div className="mx-auto max-w-lg space-y-6 py-12 text-center">
      <span className="text-6xl">🎉</span>
      <h1 className="text-2xl font-extrabold">{headline}</h1>
      <p className="text-gray-500">{subtitle}</p>
      <p className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 inline-block dark:bg-blue-900/30 dark:text-blue-300">
        {planLabel} Plan
      </p>
      <div className="grid gap-2 sm:grid-cols-2 text-left">
        {nextSteps.map(s => (
          <button key={s.href} onClick={() => onNavigate(s.href)}
            className={`flex items-center gap-3 rounded-xl border p-4 transition hover:shadow ${s.primary ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <span className="text-2xl">{s.icon}</span>
            <span className={`text-sm ${s.primary ? "font-bold" : "font-medium"}`}>{s.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
