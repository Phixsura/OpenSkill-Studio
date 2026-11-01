"use client";

interface MigrationStep { step: number; action: string; detail: string; }
interface MigrationGuideStepperProps { appName: string; steps: MigrationStep[]; effort: string; currentStep: number; }

export function MigrationGuideStepper({ appName, steps, effort, currentStep }: MigrationGuideStepperProps) {
  const effortColors = { high: "text-red-600", low: "text-green-600" };
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Migration Guide — {appName}</h3>
        <span className={`text-xs font-medium ${effortColors[effort as keyof typeof effortColors] || ""}`}>
          Effort: {effort}
        </span>
      </div>
      <ol className="mt-4 space-y-3">
        {steps.map(s => (
          <li key={s.step} className={`flex gap-3 ${s.step <= currentStep ? "opacity-60" : ""}`}>
            <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${s.step <= currentStep ? "bg-green-100 text-green-700" : s.step === currentStep + 1 ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-500"}`}>
              {s.step <= currentStep ? "✓" : s.step}
            </span>
            <div>
              <p className="text-sm font-medium">{s.action}</p>
              <p className="text-xs text-gray-500">{s.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
