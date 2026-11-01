"use client";

import { useState } from "react";

interface InstallStep {
  id: string;
  title: string;
  status: "pending" | "active" | "completed" | "error";
  description: string;
}

interface InstallConfig {
  extensionName: string;
  extensionIcon: string;
  version: string;
  permissions: string[];
  configFields: { key: string; label: string; placeholder: string; required: boolean }[];
}

export function ExtensionInstallWizard({
  config,
  onInstall,
  onCancel,
}: {
  config: InstallConfig;
  onInstall?: (configValues: Record<string, string>, acceptedPermissions: boolean) => void;
  onCancel?: () => void;
}) {
  const [step, setStep] = useState(0);
  const [permissionsAccepted, setPermissionsAccepted] = useState(false);
  const [configValues, setConfigValues] = useState<Record<string, string>>({});
  const [installing, setInstalling] = useState(false);

  const steps = ["Review Permissions", "Configure", "Install"];

  const canProceed = () => {
    if (step === 0) return permissionsAccepted;
    if (step === 1) return config.configFields
      .filter((f) => f.required)
      .every((f) => configValues[f.key]?.trim());
    return true;
  };

  const handleInstall = () => {
    setInstalling(true);
    onInstall?.(configValues, permissionsAccepted);
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 max-w-md mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <span className="text-3xl">{config.extensionIcon}</span>
        <div>
          <h2 className="font-bold">Install {config.extensionName}</h2>
          <p className="text-xs text-gray-500">v{config.version}</p>
        </div>
      </div>

      {/* Step indicator */}
      <div className="flex gap-1">
        {steps.map((s, i) => (
          <div key={s} className="flex-1">
            <div className={`h-1.5 rounded-full ${i <= step ? "bg-blue-500" : "bg-gray-200 dark:bg-gray-700"}`} />
            <div className={`text-xs mt-1 ${i === step ? "text-blue-500 font-medium" : "text-gray-400"}`}>{s}</div>
          </div>
        ))}
      </div>

      {/* Step content */}
      {step === 0 && (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">This extension requests the following permissions:</p>
          <ul className="space-y-1">
            {config.permissions.map((p) => (
              <li key={p} className="flex items-center gap-2 text-sm">
                <span className="text-yellow-500">🔑</span> {p}
              </li>
            ))}
          </ul>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={permissionsAccepted}
              onChange={(e) => setPermissionsAccepted(e.target.checked)} />
            I accept these permissions
          </label>
        </div>
      )}

      {step === 1 && (
        <div className="space-y-3">
          {config.configFields.map((f) => (
            <div key={f.key}>
              <label className="block text-sm font-medium mb-1">
                {f.label}{f.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <input
                type="text" placeholder={f.placeholder}
                value={configValues[f.key] || ""}
                onChange={(e) => setConfigValues({ ...configValues, [f.key]: e.target.value })}
                className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
              />
            </div>
          ))}
        </div>
      )}

      {step === 2 && (
        <div className="text-center space-y-2">
          {installing ? (
            <>
              <div className="text-3xl">⏳</div>
              <p className="text-sm text-gray-500">Installing {config.extensionName}...</p>
            </>
          ) : (
            <>
              <div className="text-3xl">🚀</div>
              <p className="text-sm text-gray-500">Ready to install {config.extensionName} v{config.version}</p>
            </>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <button onClick={step === 0 ? onCancel : () => setStep(step - 1)}
          className="text-sm text-gray-500 px-4 py-2">
          {step === 0 ? "Cancel" : "← Back"}
        </button>
        {step < 2 ? (
          <button onClick={() => setStep(step + 1)} disabled={!canProceed()}
            className="rounded-lg bg-blue-600 text-white px-4 py-2 text-sm font-medium disabled:opacity-50">
            Next →
          </button>
        ) : (
          <button onClick={handleInstall} disabled={installing}
            className="rounded-lg bg-green-600 text-white px-4 py-2 text-sm font-medium disabled:opacity-50">
            {installing ? "Installing..." : "✅ Install"}
          </button>
        )}
      </div>
    </div>
  );
}
