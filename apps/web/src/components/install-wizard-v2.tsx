"use client";

import { useState } from "react";

interface Step { key: string; title: string; }
interface InstallWizardV2Props { appName: string; steps: Step[]; onInstall: () => void; onCancel: () => void; }

export function InstallWizardV2({ appName, steps, onInstall, onCancel }: InstallWizardV2Props) {
  const [current, setCurrent] = useState(0);
  const isLast = current === steps.length - 1;

  return (
    <div className="mx-auto max-w-lg rounded-lg border border-gray-200 p-6 shadow-lg dark:border-gray-700">
      <h2 className="text-lg font-bold">Install {appName}</h2>
      <div className="mt-3 flex gap-1">
        {steps.map((s, i) => (
          <div key={s.key} className={`h-1 flex-1 rounded ${i <= current ? "bg-blue-600" : "bg-gray-200 dark:bg-gray-700"}`} />
        ))}
      </div>
      <p className="mt-2 text-xs text-gray-400">Step {current + 1} of {steps.length}</p>
      <h3 className="mt-4 text-lg font-semibold">{steps[current]?.title}</h3>
      <div className="mt-6 flex justify-between">
        <button onClick={current === 0 ? onCancel : () => setCurrent(current - 1)}
          className="rounded px-4 py-2 text-sm text-gray-600">{current === 0 ? "Cancel" : "Back"}</button>
        <button onClick={isLast ? onInstall : () => setCurrent(current + 1)}
          className="rounded bg-blue-600 px-6 py-2 text-sm text-white hover:bg-blue-700">
          {isLast ? "Install" : "Next"}
        </button>
      </div>
    </div>
  );
}
