"use client";

import { useState } from "react";

interface Step { step: number; title: string; duration_min: number; content: string; commands: string[]; }
interface GettingStartedTutorialProps { steps: Step[]; completedSteps: number[]; onCompleteStep: (step: number) => void; }

export function GettingStartedTutorial({ steps, completedSteps, onCompleteStep }: GettingStartedTutorialProps) {
  const [activeStep, setActiveStep] = useState(steps.find(s => !completedSteps.includes(s.step))?.step || 1);
  const currentStep = steps.find(s => s.step === activeStep);
  const pct = Math.round(completedSteps.length / steps.length * 100);

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Getting Started</h1>
        <div className="mt-2 flex items-center gap-3">
          <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-full rounded-full bg-green-500 transition-all" style={{ width: `${pct}%` }} />
          </div>
          <span className="text-sm font-medium">{pct}%</span>
        </div>
      </div>
      <div className="flex gap-4">
        <div className="w-48 space-y-1">
          {steps.map(s => (
            <button key={s.step} onClick={() => setActiveStep(s.step)}
              className={`flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm ${
                activeStep === s.step ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20"
                : completedSteps.includes(s.step) ? "text-green-600 line-through opacity-60"
                : "text-gray-600 dark:text-gray-400"}`}>
              <span>{completedSteps.includes(s.step) ? "✅" : `${s.step}.`}</span>{s.title}
            </button>
          ))}
        </div>
        {currentStep && (
          <div className="flex-1 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <h2 className="text-lg font-semibold">{currentStep.title}</h2>
            <p className="mt-1 text-xs text-gray-400">~{currentStep.duration_min} min</p>
            <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">{currentStep.content}</p>
            {currentStep.commands.length > 0 && (
              <div className="mt-3 space-y-1">
                {currentStep.commands.map((cmd, i) => (
                  <pre key={i} className="rounded bg-gray-900 px-3 py-1.5 text-xs text-green-400">{cmd}</pre>
                ))}
              </div>
            )}
            <button onClick={() => onCompleteStep(currentStep.step)}
              disabled={completedSteps.includes(currentStep.step)}
              className="mt-4 rounded bg-green-600 px-4 py-2 text-sm text-white disabled:opacity-50">
              {completedSteps.includes(currentStep.step) ? "Completed ✓" : "Mark Complete"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
