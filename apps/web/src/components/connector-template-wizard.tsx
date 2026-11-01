"use client";

import { useState } from "react";

interface ConnectorTemplate {
  id: string;
  name: string;
  icon: string;
  category: string;
  description: string;
  configFields: string[];
}

export function ConnectorTemplateWizard({
  templates,
  onCreate,
}: {
  templates: ConnectorTemplate[];
  onCreate?: (templateId: string, name: string, config: Record<string, string>) => void;
}) {
  const [step, setStep] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  const [connectorName, setConnectorName] = useState("");
  const [configValues, setConfigValues] = useState<Record<string, string>>({});

  const template = templates.find((t) => t.id === selectedTemplate);
  const categories = [...new Set(templates.map((t) => t.category))];

  const canNext = () => {
    if (step === 0) return !!selectedTemplate;
    if (step === 1) return connectorName.trim().length > 0;
    return true;
  };

  const handleCreate = () => {
    if (template) {
      onCreate?.(template.id, connectorName, configValues);
    }
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 max-w-lg mx-auto space-y-5">
      <h2 className="text-lg font-bold">🔌 New Connector</h2>

      {/* Steps */}
      <div className="flex gap-1">
        {["Choose Template", "Name & Config", "Review"].map((s, i) => (
          <div key={s} className="flex-1">
            <div className={`h-1.5 rounded-full ${i <= step ? "bg-blue-500" : "bg-gray-200 dark:bg-gray-700"}`} />
            <div className={`text-xs mt-1 ${i === step ? "text-blue-500 font-medium" : "text-gray-400"}`}>{s}</div>
          </div>
        ))}
      </div>

      {/* Step 0: Template selection */}
      {step === 0 && (
        <div className="space-y-2">
          {categories.map((cat) => (
            <div key={cat}>
              <div className="text-xs font-semibold text-gray-400 uppercase mb-1">{cat}</div>
              {templates.filter((t) => t.category === cat).map((t) => (
                <button key={t.id} onClick={() => setSelectedTemplate(t.id)}
                  className={`w-full text-left flex items-center gap-3 p-3 rounded-lg border mb-1 ${
                    selectedTemplate === t.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"
                  }`}>
                  <span className="text-2xl">{t.icon}</span>
                  <div>
                    <div className="font-medium text-sm">{t.name}</div>
                    <div className="text-xs text-gray-400">{t.description}</div>
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Step 1: Name & Config */}
      {step === 1 && template && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">Connector Name *</label>
            <input type="text" value={connectorName} onChange={(e) => setConnectorName(e.target.value)}
              placeholder={`My ${template.name} Connector`}
              className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
          </div>
          {template.configFields.map((field) => (
            <div key={field}>
              <label className="block text-sm font-medium mb-1">{field}</label>
              <input type="text" value={configValues[field] || ""}
                onChange={(e) => setConfigValues({ ...configValues, [field]: e.target.value })}
                className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
            </div>
          ))}
        </div>
      )}

      {/* Step 2: Review */}
      {step === 2 && template && (
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2"><span className="text-2xl">{template.icon}</span><span className="font-bold">{connectorName}</span></div>
          <div className="text-gray-500">Template: {template.name}</div>
          {Object.entries(configValues).filter(([, v]) => v).map(([k, v]) => (
            <div key={k} className="text-xs"><span className="text-gray-400">{k}:</span> {v}</div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <button onClick={() => step > 0 ? setStep(step - 1) : null}
          className="text-sm text-gray-500 px-4 py-2">{step === 0 ? "" : "← Back"}</button>
        {step < 2 ? (
          <button onClick={() => setStep(step + 1)} disabled={!canNext()}
            className="rounded-lg bg-blue-600 text-white px-4 py-2 text-sm font-medium disabled:opacity-50">Next →</button>
        ) : (
          <button onClick={handleCreate}
            className="rounded-lg bg-green-600 text-white px-4 py-2 text-sm font-medium">🔌 Create Connector</button>
        )}
      </div>
    </div>
  );
}
