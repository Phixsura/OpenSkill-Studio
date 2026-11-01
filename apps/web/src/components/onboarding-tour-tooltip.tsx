"use client";

interface TourStep { step: number; id: string; title: string; description: string;
  target: string | null; position: string; completed: boolean; }
interface OnboardingTourTooltipProps { currentStep: TourStep | null; totalSteps: number;
  completedCount: number; onNext: () => void; onSkip: () => void; }

export function OnboardingTourTooltip({ currentStep, totalSteps, completedCount, onNext, onSkip }: OnboardingTourTooltipProps) {
  if (!currentStep) return null;
  const isLast = currentStep.step === totalSteps;
  return (
    <div className="rounded-lg border border-blue-300 bg-blue-50 p-4 shadow-lg dark:border-blue-700 dark:bg-blue-900/20">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-blue-500">Step {currentStep.step} of {totalSteps}</p>
          <h3 className="mt-1 font-bold">{currentStep.title}</h3>
          <p className="mt-0.5 text-sm text-gray-500">{currentStep.description}</p>
        </div>
        <button onClick={onSkip} className="text-xs text-gray-400">✕</button>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <div className="flex gap-1">
          {Array.from({ length: totalSteps }, (_, i) => (
            <div key={i} className={`h-1.5 w-4 rounded-full ${i < completedCount ? "bg-blue-500" : i === completedCount ? "bg-blue-300" : "bg-gray-200 dark:bg-gray-700"}`} />
          ))}
        </div>
        <button onClick={onNext} className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">
          {isLast ? "Finish" : "Next"}
        </button>
      </div>
    </div>
  );
}
