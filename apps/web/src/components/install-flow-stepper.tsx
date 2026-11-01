"use client";

interface InstallFlowStepperProps { steps: string[]; currentStep: number; appName: string; }

const STEP_LABELS: Record<string, string> = { review_permissions: "Review Permissions", configure: "Configure", confirm_install: "Confirm Install" };

export function InstallFlowStepper({ steps, currentStep, appName }: InstallFlowStepperProps) {
  return (
    <div>
      <h3 className="mb-3 font-semibold">Install {appName}</h3>
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium ${
              i < currentStep ? "bg-green-500 text-white" : i === currentStep ? "bg-blue-600 text-white" : "bg-gray-200"
            }`}>{i < currentStep ? "✓" : i + 1}</div>
            <span className={`text-sm ${i === currentStep ? "font-semibold" : "text-gray-500"}`}>{STEP_LABELS[s] ?? s}</span>
            {i < steps.length - 1 && <div className={`h-0.5 w-6 ${i < currentStep ? "bg-green-500" : "bg-gray-200"}`} />}
          </div>
        ))}
      </div>
    </div>
  );
}
