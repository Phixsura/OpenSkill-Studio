"use client";

interface WelcomeScreenProps { greeting: string; message: string; type: string;
  steps?: string[]; ctaLabel: string; onCta: () => void; }

export function WelcomeScreen({ greeting, message, type, steps, ctaLabel, onCta }: WelcomeScreenProps) {
  return (
    <div className="max-w-lg mx-auto text-center py-12">
      <h1 className="text-2xl font-bold mb-2">{greeting}</h1>
      <p className="text-sm text-gray-500 mb-6">{message}</p>
      {type === "new_user" && steps && (
        <div className="text-left mb-6 space-y-2">
          {steps.map((s, i) => (
            <div key={i} className="flex items-center gap-2 text-sm bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2">
              <span className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center">{i + 1}</span>
              {s}
            </div>
          ))}
        </div>
      )}
      <button onClick={onCta}
        className="px-8 py-3 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700">{ctaLabel}</button>
    </div>
  );
}
