"use client";

import { useState } from "react";

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: string;
  completed: boolean;
  action?: string;
}

export function DeveloperOnboardingWizard({
  steps,
  developerName,
  onStepAction,
  onComplete,
}: {
  steps: OnboardingStep[];
  developerName: string;
  onStepAction?: (stepId: string) => void;
  onComplete?: () => void;
}) {
  const [currentStep, setCurrentStep] = useState(
    steps.findIndex((s) => !s.completed)
  );

  const completedCount = steps.filter((s) => s.completed).length;
  const progress = Math.round((completedCount / steps.length) * 100);
  const allDone = completedCount === steps.length;

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 space-y-5 max-w-lg mx-auto">
      <div className="text-center">
        <h2 className="text-xl font-bold">👋 Welcome, {developerName}!</h2>
        <p className="text-sm text-gray-500 mt-1">Complete these steps to start building extensions</p>
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{completedCount} of {steps.length} complete</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="h-2 rounded-full bg-green-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-2">
        {steps.map((step, i) => (
          <button
            key={step.id}
            onClick={() => setCurrentStep(i)}
            className={`w-full text-left flex items-center gap-3 p-3 rounded-lg border transition ${
              currentStep === i
                ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10"
                : "border-transparent dark:border-gray-800"
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
              step.completed
                ? "bg-green-100 dark:bg-green-900/30 text-green-600"
                : currentStep === i
                  ? "bg-blue-100 dark:bg-blue-900/30 text-blue-600"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-400"
            }`}>
              {step.completed ? "✓" : step.icon}
            </div>
            <div className="flex-1">
              <div className={`text-sm font-medium ${step.completed ? "line-through text-gray-400" : ""}`}>
                {step.title}
              </div>
              {currentStep === i && (
                <p className="text-xs text-gray-500 mt-0.5">{step.description}</p>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Action */}
      {!allDone && steps[currentStep] && !steps[currentStep].completed && (
        <button
          onClick={() => onStepAction?.(steps[currentStep].id)}
          className="w-full rounded-lg bg-blue-600 text-white py-2.5 text-sm font-medium"
        >
          {steps[currentStep].action || `Complete: ${steps[currentStep].title}`}
        </button>
      )}

      {allDone && (
        <div className="text-center space-y-3">
          <div className="text-3xl">🎉</div>
          <p className="font-bold text-green-600 dark:text-green-400">All set! You're ready to build.</p>
          <button
            onClick={() => onComplete?.()}
            className="rounded-lg bg-green-600 text-white px-6 py-2 text-sm font-medium"
          >
            Start Building →
          </button>
        </div>
      )}
    </div>
  );
}
