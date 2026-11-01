"use client";

import { useState } from "react";

interface Step { key: string; title: string; type: string; completed: boolean; current: boolean; required: boolean; }
interface OnboardingFlowWizardProps { steps: Step[]; progressPct: number; currentStep: Step | null;
  tips: string[]; onCompleteStep: (key: string) => void; onSkip: () => void; }

export function OnboardingFlowWizard({ steps, progressPct, currentStep, tips, onCompleteStep, onSkip }: OnboardingFlowWizardProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Get Started</h1>
        <div className="mt-2 flex items-center gap-3">
          <div className="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
          </div>
          <span className="text-sm font-medium">{progressPct}%</span>
        </div>
      </div>
      <div className="space-y-2">
        {steps.map((s, i) => (
          <div key={s.key} className={`flex items-center gap-3 rounded-lg border p-4 ${
            s.current ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" :
            s.completed ? "border-green-200 opacity-60" : "border-gray-200 dark:border-gray-700"}`}>
            <span className="flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold">
              {s.completed ? "✅" : s.current ? "👉" : `${i + 1}`}
            </span>
            <div className="flex-1">
              <p className={`font-medium ${s.completed ? "line-through" : ""}`}>{s.title}</p>
              {s.required && !s.completed && <span className="text-xs text-red-500">Required</span>}
            </div>
            {s.current && (
              <button onClick={() => onCompleteStep(s.key)}
                className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">Start</button>
            )}
          </div>
        ))}
      </div>
      {tips.length > 0 && (
        <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
          <p className="text-xs font-semibold text-blue-700">💡 Tips</p>
          {tips.map((t, i) => <p key={i} className="text-xs text-blue-600">• {t}</p>)}
        </div>
      )}
    </div>
  );
}
