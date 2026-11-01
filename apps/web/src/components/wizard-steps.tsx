"use client";

interface WizardStepsProps {
  steps: string[];
  currentStep: number;
}

export function WizardSteps({ steps, currentStep }: WizardStepsProps) {
  return (
    <div className="flex items-center gap-1">
      {steps.map((step, i) => (
        <div key={i} className="flex items-center">
          <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${
            i < currentStep ? "bg-green-500 text-white" :
            i === currentStep ? "bg-blue-600 text-white" :
            "bg-gray-200 text-gray-500 dark:bg-gray-700"
          }`}>
            {i < currentStep ? "✓" : i + 1}
          </div>
          <span className={`ml-1 text-xs ${i === currentStep ? "font-semibold" : "text-gray-400"}`}>{step}</span>
          {i < steps.length - 1 && <div className={`mx-2 h-0.5 w-8 ${i < currentStep ? "bg-green-500" : "bg-gray-200 dark:bg-gray-700"}`} />}
        </div>
      ))}
    </div>
  );
}
