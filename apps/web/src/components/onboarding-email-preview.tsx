"use client";

interface Step { step: number; title: string; url: string; }
interface OnboardingEmailPreviewProps { subject: string; developerName: string; plan: string;
  steps: Step[]; ctaLabel: string; ctaUrl: string; }

export function OnboardingEmailPreview({ subject, developerName, plan, steps, ctaLabel, ctaUrl }: OnboardingEmailPreviewProps) {
  return (
    <div className="mx-auto max-w-md rounded-lg border shadow dark:border-gray-700">
      <div className="border-b bg-gray-50 px-4 py-2 dark:border-gray-700 dark:bg-gray-800">
        <p className="text-xs text-gray-400">Subject:</p>
        <p className="text-sm font-medium">{subject}</p>
      </div>
      <div className="space-y-4 p-6">
        <div className="text-center">
          <p className="text-3xl">🎉</p>
          <h1 className="mt-2 text-xl font-bold">Welcome, {developerName}!</h1>
          <p className="mt-1 text-sm text-gray-400">You&apos;re on the <strong className="capitalize">{plan}</strong> plan</p>
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium">Here&apos;s how to get started:</p>
          {steps.map(s => (
            <div key={s.step} className="flex items-center gap-2 rounded bg-gray-50 p-2 dark:bg-gray-800">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs text-white">{s.step}</span>
              <span className="text-sm">{s.title}</span>
            </div>
          ))}
        </div>
        <a href={ctaUrl} className="block rounded-lg bg-blue-600 py-3 text-center text-sm font-bold text-white">
          {ctaLabel}
        </a>
      </div>
    </div>
  );
}
