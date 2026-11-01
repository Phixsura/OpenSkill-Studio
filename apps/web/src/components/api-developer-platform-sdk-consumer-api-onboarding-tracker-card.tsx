"use client";

import { useState } from "react";

interface Step {
  stepId: string;
  name: string;
  completed: boolean;
}

export default function OnboardingTrackerCard() {
  const [steps] = useState<Step[]>([
    { stepId: "s1", name: "Create Account", completed: true },
    { stepId: "s2", name: "Generate API Key", completed: true },
    { stepId: "s3", name: "Make First Call", completed: false },
    { stepId: "s4", name: "Read Documentation", completed: false },
  ]);

  const completed = steps.filter((s) => s.completed).length;
  const pct = Math.round((completed / steps.length) * 100);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Onboarding Tracker
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Step-based onboarding with progress tracking
      </p>

      <div className="mt-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-zinc-700 dark:text-zinc-300">{pct}% complete</span>
          <span className="text-zinc-400">{completed}/{steps.length}</span>
        </div>
        <div className="mt-1 h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
          <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div className="mt-4 space-y-2">
        {steps.map((s) => (
          <div key={s.stepId} className="flex items-center gap-2">
            <span className={`flex h-5 w-5 items-center justify-center rounded-full text-xs ${s.completed ? "bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400" : "bg-zinc-100 text-zinc-400 dark:bg-zinc-800"}`}>
              {s.completed ? "✓" : "·"}
            </span>
            <span className={`text-sm ${s.completed ? "text-zinc-500 line-through" : "text-zinc-900 dark:text-zinc-100"}`}>
              {s.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
