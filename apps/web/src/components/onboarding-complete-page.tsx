"use client";

interface NextStep { label: string; url: string; icon: string; }
interface OnboardingCompletePageProps { message: string; achievements: string[]; nextSteps: NextStep[]; }

export function OnboardingCompletePage({ message, achievements, nextSteps }: OnboardingCompletePageProps) {
  return (
    <div className="mx-auto max-w-lg space-y-6 py-12 text-center">
      <div className="text-6xl">🎉</div>
      <h1 className="text-2xl font-bold">{message}</h1>
      <div className="rounded-lg bg-green-50 p-4 dark:bg-green-900/20">
        <h3 className="text-sm font-semibold text-green-700 dark:text-green-300">What you accomplished</h3>
        <ul className="mt-2 space-y-1">
          {achievements.map((a, i) => (
            <li key={i} className="text-sm text-green-600">✅ {a}</li>
          ))}
        </ul>
      </div>
      <div>
        <h3 className="text-sm font-semibold text-gray-500">What to do next</h3>
        <div className="mt-3 grid grid-cols-2 gap-3">
          {nextSteps.map(s => (
            <a key={s.label} href={s.url}
              className="rounded-lg border border-gray-200 p-3 text-center transition hover:shadow-md dark:border-gray-700">
              <span className="text-xl">{s.icon}</span>
              <p className="mt-1 text-sm font-medium">{s.label}</p>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
