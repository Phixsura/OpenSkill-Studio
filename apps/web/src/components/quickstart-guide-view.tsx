"use client";

interface Step { step: number; title: string; code: string; language: string; }
interface QuickstartGuideViewProps { appName: string; sdk: string; steps: Step[];
  estimatedTimeMin: number; onCopy: (code: string) => void; }

export function QuickstartGuideView({ appName, sdk, steps, estimatedTimeMin, onCopy }: QuickstartGuideViewProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold">Quick Start: {appName}</h2>
        <p className="text-sm text-gray-400">{sdk} SDK · ~{estimatedTimeMin} min</p>
      </div>
      {steps.map(s => (
        <div key={s.step}>
          <h3 className="flex items-center gap-2 font-semibold">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs text-white">{s.step}</span>
            {s.title}
          </h3>
          <div className="relative mt-2">
            <pre className="overflow-x-auto rounded-lg bg-gray-900 p-4 font-mono text-xs text-green-400">
              {s.code}
            </pre>
            <button onClick={() => onCopy(s.code)}
              className="absolute right-2 top-2 rounded bg-gray-700 px-2 py-0.5 text-xs text-gray-300">
              Copy
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
