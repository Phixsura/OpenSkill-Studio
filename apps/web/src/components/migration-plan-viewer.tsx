"use client";

interface MigrationStep {
  action: string;
  reason?: string;
  breaking?: boolean;
  count?: number;
}

interface MigrationPlanViewerProps {
  fromVersion: string;
  toVersion: string;
  breaking: boolean;
  steps: MigrationStep[];
  affectedInstallations: number;
  requiresConsent: boolean;
}

const ACTION_ICONS: Record<string, string> = {
  request_consent: "🔑", warn_removal: "⚠️", validate_configs: "📋",
  update_sandbox: "⚙️", upgrade_installations: "🚀",
};

export function MigrationPlanViewer({ fromVersion, toVersion, breaking, steps, affectedInstallations, requiresConsent }: MigrationPlanViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">Migration: {fromVersion} → {toVersion}</h4>
        <div className="flex gap-2">
          {breaking && <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800">Breaking</span>}
          {requiresConsent && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-800">Consent Required</span>}
        </div>
      </div>
      <p className="mb-3 text-sm text-gray-500">{affectedInstallations} installation{affectedInstallations !== 1 ? "s" : ""} affected</p>
      <ol className="space-y-2">
        {steps.map((step, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <span className="mt-0.5 font-mono text-xs text-gray-400">{i + 1}.</span>
            <span>{ACTION_ICONS[step.action] ?? "▶️"}</span>
            <div>
              <span className="font-medium">{step.action.replace(/_/g, " ")}</span>
              {step.reason && <p className="text-xs text-gray-500">{step.reason}</p>}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
