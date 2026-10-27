"use client";

import { useState } from "react";

interface Permission {
  scope: string;
  description: string;
  risk: "low" | "medium" | "high" | "critical";
}

interface ConfigField {
  name: string;
  label: string;
  type: "string" | "boolean" | "url" | "enum";
  required: boolean;
  default_value: string;
  description: string;
  enum_values?: string[];
}

interface AppInfo {
  id: string;
  name: string;
  icon: string;
  publisher: string;
  version: string;
  description: string;
  permissions: Permission[];
  config_fields: ConfigField[];
}

interface AppInstallWizardProps {
  app: AppInfo;
  onInstall: (config: Record<string, string>) => void;
  onCancel: () => void;
  installing?: boolean;
}

type Step = "review" | "permissions" | "configure" | "confirm";

const STEPS: { key: Step; label: string }[] = [
  { key: "review", label: "Review" },
  { key: "permissions", label: "Permissions" },
  { key: "configure", label: "Configure" },
  { key: "confirm", label: "Install" },
];

const RISK_COLORS: Record<string, string> = {
  low: "text-green-600 dark:text-green-400",
  medium: "text-yellow-600 dark:text-yellow-400",
  high: "text-orange-600 dark:text-orange-400",
  critical: "text-red-600 dark:text-red-400",
};

function StepIndicator({ current, steps }: { current: Step; steps: typeof STEPS }) {
  const idx = steps.findIndex((s) => s.key === current);
  return (
    <div className="flex items-center gap-1" role="navigation" aria-label="Install steps">
      {steps.map((s, i) => (
        <div key={s.key} className="flex items-center">
          <div
            className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
              i <= idx ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-500 dark:bg-gray-700"
            }`}
          >
            {i + 1}
          </div>
          <span
            className={`ml-1 text-xs ${i <= idx ? "font-medium" : "text-gray-400"} ${i < steps.length - 1 ? "mr-3" : ""}`}
          >
            {s.label}
          </span>
          {i < steps.length - 1 && (
            <div
              className={`mx-1 h-px w-6 ${i < idx ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}
            />
          )}
        </div>
      ))}
    </div>
  );
}

export function AppInstallWizard({ app, onInstall, onCancel, installing }: AppInstallWizardProps) {
  const [step, setStep] = useState<Step>("review");
  const [config, setConfig] = useState<Record<string, string>>(() => {
    const defaults: Record<string, string> = {};
    for (const f of app.config_fields) {
      defaults[f.name] = f.default_value;
    }
    return defaults;
  });
  const [permissionsAccepted, setPermissionsAccepted] = useState(false);

  const stepIdx = STEPS.findIndex((s) => s.key === step);
  const canNext =
    step === "review" || (step === "permissions" && permissionsAccepted) || step === "configure";
  const isLast = step === "confirm";

  function next() {
    if (stepIdx < STEPS.length - 1) {
      setStep(STEPS[stepIdx + 1].key);
    }
  }

  function back() {
    if (stepIdx > 0) {
      setStep(STEPS[stepIdx - 1].key);
    }
  }

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-5 py-4 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{app.icon}</span>
          <div>
            <h2 className="font-semibold">Install {app.name}</h2>
            <p className="text-xs text-gray-500">
              v{app.version} by {app.publisher}
            </p>
          </div>
        </div>
        <div className="mt-3">
          <StepIndicator current={step} steps={STEPS} />
        </div>
      </div>

      {/* Step content */}
      <div className="min-h-[200px] px-5 py-4">
        {step === "review" && (
          <div>
            <h3 className="text-sm font-semibold">About this app</h3>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{app.description}</p>
            <div className="mt-3 flex gap-4 text-xs text-gray-500">
              <span>{app.permissions.length} permissions</span>
              <span>{app.config_fields.length} config fields</span>
            </div>
          </div>
        )}

        {step === "permissions" && (
          <div>
            <h3 className="text-sm font-semibold">Requested Permissions</h3>
            <ul className="mt-2 space-y-2">
              {app.permissions.map((p) => (
                <li key={p.scope} className="flex items-start gap-2 text-sm">
                  <span className={`mt-0.5 text-xs font-bold ${RISK_COLORS[p.risk]}`}>
                    {p.risk.toUpperCase()}
                  </span>
                  <div>
                    <code className="text-xs">{p.scope}</code>
                    <p className="text-xs text-gray-500">{p.description}</p>
                  </div>
                </li>
              ))}
            </ul>
            <label className="mt-4 flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={permissionsAccepted}
                onChange={(e) => setPermissionsAccepted(e.target.checked)}
                className="rounded"
              />
              <span>I accept these permissions</span>
            </label>
          </div>
        )}

        {step === "configure" && (
          <div>
            <h3 className="text-sm font-semibold">Configuration</h3>
            {app.config_fields.length === 0 ? (
              <p className="mt-2 text-sm text-gray-500">No configuration needed.</p>
            ) : (
              <div className="mt-2 space-y-3">
                {app.config_fields.map((f) => (
                  <div key={f.name}>
                    <label className="text-xs font-medium">
                      {f.label}
                      {f.required && <span className="text-red-500"> *</span>}
                    </label>
                    {f.type === "boolean" ? (
                      <input
                        type="checkbox"
                        checked={config[f.name] === "true"}
                        onChange={(e) =>
                          setConfig({ ...config, [f.name]: e.target.checked ? "true" : "false" })
                        }
                        className="ml-2 rounded"
                      />
                    ) : f.type === "enum" && f.enum_values ? (
                      <select
                        value={config[f.name] ?? ""}
                        onChange={(e) => setConfig({ ...config, [f.name]: e.target.value })}
                        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800"
                      >
                        {f.enum_values.map((v) => (
                          <option key={v} value={v}>
                            {v}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={config[f.name] ?? ""}
                        onChange={(e) => setConfig({ ...config, [f.name]: e.target.value })}
                        placeholder={f.description}
                        className="mt-1 block w-full rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800"
                      />
                    )}
                    <p className="mt-0.5 text-[10px] text-gray-400">{f.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {step === "confirm" && (
          <div className="text-center">
            <span className="text-4xl">{app.icon}</span>
            <h3 className="mt-2 font-semibold">Ready to install {app.name}</h3>
            <p className="mt-1 text-sm text-gray-500">
              {app.permissions.length} permissions granted • {Object.keys(config).length} config
              values set
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-gray-200 px-5 py-3 dark:border-gray-700">
        <button
          onClick={stepIdx === 0 ? onCancel : back}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          {stepIdx === 0 ? "Cancel" : "Back"}
        </button>
        {isLast ? (
          <button
            onClick={() => onInstall(config)}
            disabled={installing}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {installing ? "Installing…" : "Install App"}
          </button>
        ) : (
          <button
            onClick={next}
            disabled={!canNext}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
