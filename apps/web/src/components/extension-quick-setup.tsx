"use client";

import { useState } from "react";

interface SetupStep {
  id: string;
  title: string;
  command: string;
  description: string;
}

export function ExtensionQuickSetup({
  extensionName,
  steps,
  packageManager,
}: {
  extensionName: string;
  steps: SetupStep[];
  packageManager?: "npm" | "pnpm" | "yarn";
}) {
  const [currentStep, setCurrentStep] = useState(0);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const pm = packageManager || "npm";

  const copyCommand = (stepId: string, command: string) => {
    navigator.clipboard?.writeText(command).catch(() => {});
    setCopiedId(stepId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 max-w-lg space-y-5">
      <div>
        <h2 className="text-lg font-bold">⚡ Quick Setup</h2>
        <p className="text-sm text-gray-500">Get {extensionName} running in minutes</p>
      </div>

      {/* Package manager selector */}
      <div className="flex gap-1 text-xs">
        {(["npm", "pnpm", "yarn"] as const).map((p) => (
          <span key={p} className={`px-2 py-1 rounded ${pm === p ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {p}
          </span>
        ))}
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {steps.map((step, i) => (
          <div key={step.id} className={`rounded-lg border p-3 transition ${
            i === currentStep ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"
          }`}>
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-6 h-6 rounded-full text-xs flex items-center justify-center font-bold ${
                i < currentStep ? "bg-green-500 text-white" : i === currentStep ? "bg-blue-500 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-500"
              }`}>
                {i < currentStep ? "✓" : i + 1}
              </span>
              <span className="text-sm font-medium">{step.title}</span>
            </div>
            <p className="text-xs text-gray-500 ml-8 mb-2">{step.description}</p>
            <div className="ml-8 flex items-center gap-2">
              <code className="flex-1 bg-gray-900 text-green-400 text-xs px-3 py-2 rounded font-mono">
                $ {step.command.replace("npm", pm)}
              </code>
              <button onClick={() => copyCommand(step.id, step.command.replace("npm", pm))}
                className="text-xs text-gray-400 hover:text-gray-600 px-2 py-2 border dark:border-gray-700 rounded">
                {copiedId === step.id ? "✅" : "📋"}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
          className="text-sm text-gray-500 disabled:opacity-30">← Previous</button>
        <button onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
          disabled={currentStep === steps.length - 1}
          className="text-sm text-blue-500 disabled:opacity-30">Next →</button>
      </div>
    </div>
  );
}
