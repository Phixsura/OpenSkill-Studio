"use client";

interface Feature { title: string; description: string; icon: string; }
interface NextStep { title: string; href: string; icon: string; }
interface WelcomeScreenProps { appName: string; appIcon: string; headline: string;
  features: Feature[]; nextSteps: NextStep[];
  onDismiss: () => void; onNavigate: (href: string) => void; }

export function WelcomeScreen({ appName, appIcon, headline, features, nextSteps, onDismiss, onNavigate }: WelcomeScreenProps) {
  return (
    <div className="mx-auto max-w-lg space-y-6 py-8 text-center">
      <span className="text-6xl">{appIcon}</span>
      <h1 className="text-2xl font-extrabold">{headline}</h1>
      <div className="grid gap-3">
        {features.map(f => (
          <div key={f.title} className="flex items-center gap-3 rounded-lg border p-3 text-left dark:border-gray-700">
            <span className="text-2xl">{f.icon}</span>
            <div><p className="text-sm font-medium">{f.title}</p><p className="text-xs text-gray-400">{f.description}</p></div>
          </div>
        ))}
      </div>
      <div>
        <p className="text-sm font-semibold mb-2">Next Steps</p>
        <div className="flex justify-center gap-2">
          {nextSteps.map(s => (
            <button key={s.href} onClick={() => onNavigate(s.href)}
              className="flex items-center gap-1.5 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
              <span>{s.icon}</span>{s.title}
            </button>
          ))}
        </div>
      </div>
      <button onClick={onDismiss} className="text-sm text-gray-400 hover:text-gray-600">Skip for now →</button>
    </div>
  );
}
