"use client";

interface Permission { name: string; description: string; risk: string; }
interface InstallStep { id: string; title: string; status: string; }
interface InstallFlowWizardProps { appName: string; appIcon: string;
  developer: string; permissions: Permission[]; steps: InstallStep[];
  currentStep: number; hasDangerous: boolean;
  onAdvance: () => void; onCancel: () => void; }

const RISK_STYLE: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-red-600",
};

export function InstallFlowWizard({ appName, appIcon, developer, permissions,
  steps, currentStep, hasDangerous, onAdvance, onCancel }: InstallFlowWizardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 max-w-lg">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">{appIcon}</span>
        <div>
          <h3 className="font-bold">Install {appName}</h3>
          <p className="text-xs text-gray-400">By {developer}</p>
        </div>
      </div>
      <div className="flex gap-1 mb-4">
        {steps.map((s, i) => (
          <div key={s.id} className={`flex-1 h-1.5 rounded-full ${
            s.status === "completed" ? "bg-green-500" :
            s.status === "current" ? "bg-blue-500" : "bg-gray-200 dark:bg-gray-700"
          }`} />
        ))}
      </div>
      <p className="text-sm font-medium mb-2">{steps[currentStep]?.title}</p>
      {currentStep === 0 && permissions.length > 0 && (
        <div className="space-y-1 mb-4">
          {permissions.map(p => (
            <div key={p.name} className="flex justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
              <span>{p.name}</span>
              <span className={`text-xs ${RISK_STYLE[p.risk] || ""}`}>{p.risk}</span>
            </div>
          ))}
          {hasDangerous && <p className="text-xs text-red-500">⚠️ This app requests high-risk permissions</p>}
        </div>
      )}
      <div className="flex gap-2">
        <button onClick={onCancel} className="flex-1 py-2 border rounded text-sm">Cancel</button>
        <button onClick={onAdvance} className="flex-1 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
          {currentStep === steps.length - 1 ? "Activate" : "Continue"}
        </button>
      </div>
    </div>
  );
}
