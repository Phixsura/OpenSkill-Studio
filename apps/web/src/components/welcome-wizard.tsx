"use client";

import { useState } from "react";

interface Step { title: string; content?: string; action?: string; }
interface WelcomeWizardProps { steps: Step[]; experience: string; onComplete: () => void; }

export function WelcomeWizard({ steps, experience, onComplete }: WelcomeWizardProps) {
  const [current, setCurrent] = useState(0);
  const step = steps[current];
  const isLast = current === steps.length - 1;

  return (
    <div className="mx-auto max-w-lg rounded-lg border border-gray-200 p-8 shadow-lg dark:border-gray-700">
      <div className="mb-4 flex justify-between text-xs text-gray-400">
        <span>{experience} track</span>
        <span>{current + 1} / {steps.length}</span>
      </div>
      <div className="mb-2 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${((current + 1) / steps.length) * 100}%` }} />
      </div>
      <h2 className="mt-6 text-xl font-bold">{step?.title}</h2>
      {step?.content && <p className="mt-2 text-sm text-gray-500">{step.content}</p>}
      <div className="mt-8 flex justify-between">
        <button onClick={() => setCurrent(Math.max(0, current - 1))} disabled={current === 0}
          className="rounded px-4 py-2 text-sm text-gray-500 disabled:opacity-30">Back</button>
        <button onClick={() => isLast ? onComplete() : setCurrent(current + 1)}
          className="rounded bg-blue-600 px-6 py-2 text-sm text-white hover:bg-blue-700">
          {isLast ? "Get Started! 🚀" : "Next →"}
        </button>
      </div>
    </div>
  );
}
