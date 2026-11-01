"use client";

import { useState } from "react";

interface WorkflowStep {
  id: string;
  action: string;
  params: Record<string, string>;
}

interface WorkflowDef {
  name: string;
  trigger: string;
  steps: WorkflowStep[];
}

export function WorkflowBuilderPanel({
  onSave,
}: {
  onSave?: (workflow: WorkflowDef) => void;
}) {
  const [name, setName] = useState("");
  const [trigger, setTrigger] = useState("event");
  const [steps, setSteps] = useState<WorkflowStep[]>([
    { id: "step-1", action: "", params: {} },
  ]);

  const addStep = () => {
    setSteps([...steps, { id: `step-${steps.length + 1}`, action: "", params: {} }]);
  };

  const removeStep = (id: string) => {
    if (steps.length > 1) {
      setSteps(steps.filter((s) => s.id !== id));
    }
  };

  const updateAction = (id: string, action: string) => {
    setSteps(steps.map((s) => (s.id === id ? { ...s, action } : s)));
  };

  const handleSave = () => {
    if (name && steps.every((s) => s.action)) {
      onSave?.({ name, trigger, steps });
    }
  };

  const triggerOptions = [
    { value: "event", label: "🔔 Event" },
    { value: "webhook", label: "🌐 Webhook" },
    { value: "schedule", label: "⏰ Schedule" },
    { value: "manual", label: "👆 Manual" },
  ];

  const actionOptions = [
    "notify", "build", "test", "deploy", "approve",
    "send_email", "call_api", "transform_data",
  ];

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 space-y-4">
      <h2 className="text-lg font-bold">⚙️ Workflow Builder</h2>

      <div>
        <label className="block text-sm font-medium mb-1">Workflow Name</label>
        <input
          type="text"
          placeholder="My Automation..."
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Trigger Type</label>
        <div className="flex gap-2">
          {triggerOptions.map((t) => (
            <button
              key={t.value}
              onClick={() => setTrigger(t.value)}
              className={`rounded-lg px-3 py-1.5 text-sm ${
                trigger === t.value
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Steps</label>
        <div className="space-y-2">
          {steps.map((step, i) => (
            <div key={step.id} className="flex items-center gap-2">
              <span className="text-xs text-gray-400 w-6">{i + 1}.</span>
              <select
                value={step.action}
                onChange={(e) => updateAction(step.id, e.target.value)}
                className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
              >
                <option value="">Select action...</option>
                {actionOptions.map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
              <button
                onClick={() => removeStep(step.id)}
                className="text-red-400 hover:text-red-600 text-sm px-2"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
        <button
          onClick={addStep}
          className="mt-2 text-sm text-blue-500 hover:text-blue-700"
        >
          + Add Step
        </button>
      </div>

      <button
        onClick={handleSave}
        className="w-full rounded-lg bg-green-600 text-white py-2 text-sm font-medium hover:bg-green-700"
      >
        💾 Save Workflow
      </button>
    </div>
  );
}
