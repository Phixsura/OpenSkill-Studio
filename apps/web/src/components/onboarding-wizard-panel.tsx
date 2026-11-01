"use client";

interface WizardStep { stepId: string; title: string; description: string; required: boolean; completed: boolean; skipped: boolean; }
interface Progress { currentStep: number; totalSteps: number; percent: number; isComplete: boolean; }

export function OnboardingWizardPanel({
  steps, progress, onComplete, onSkip, onBack,
}: {
  steps: WizardStep[]; progress: Progress;
  onComplete?: () => void; onSkip?: () => void; onBack?: () => void;
}) {
  const current = steps[progress.currentStep];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🧙 Setup Wizard</h2>

      {/* Progress bar */}
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${progress.percent}%` }} />
      </div>

      {/* Steps indicator */}
      <div className="flex gap-1">
        {steps.map((s, i) => (
          <div key={s.stepId} className={`flex-1 h-1.5 rounded-full ${
            s.completed ? "bg-green-500" : s.skipped ? "bg-gray-300" : i === progress.currentStep ? "bg-blue-500" : "bg-gray-200 dark:bg-gray-700"
          }`} />
        ))}
      </div>

      {progress.isComplete ? (
        <div className="text-center py-8">
          <span className="text-4xl">🎉</span>
          <p className="text-lg font-bold mt-2">Setup Complete!</p>
        </div>
      ) : current && (
        <div className="rounded-xl border dark:border-gray-700 p-6 text-center">
          <span className="text-xs text-gray-500">Step {progress.currentStep + 1}/{progress.totalSteps}</span>
          <h3 className="text-lg font-bold mt-1">{current.title}</h3>
          <p className="text-sm text-gray-500 mt-1">{current.description}</p>
          <div className="flex gap-2 justify-center mt-4">
            {progress.currentStep > 0 && <button onClick={onBack} className="text-sm bg-gray-100 dark:bg-gray-800 px-4 py-2 rounded-lg">Back</button>}
            {!current.required && <button onClick={onSkip} className="text-sm text-gray-500 px-4 py-2">Skip</button>}
            <button onClick={onComplete} className="text-sm bg-blue-600 text-white px-6 py-2 rounded-lg">Continue</button>
          </div>
        </div>
      )}
    </div>
  );
}
