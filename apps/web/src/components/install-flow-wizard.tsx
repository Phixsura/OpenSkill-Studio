"use client";
import { useState } from "react";

interface InstallStep { step: string; label: string; }
const STEPS: InstallStep[] = [
  { step: "consent", label: "Permissions" },
  { step: "configure", label: "Configure" },
  { step: "install", label: "Install" },
  { step: "complete", label: "Done" },
];

export function InstallFlowWizard({ currentStep, extensionName, permissions, onGrant, onConfigure, onComplete }: {
  currentStep: string; extensionName: string; permissions: string[];
  onGrant?: (perms: string[]) => void; onConfigure?: (config: Record<string, string>) => void; onComplete?: () => void;
}) {
  const [granted, setGranted] = useState<Set<string>>(new Set());
  const stepIdx = STEPS.findIndex(s => s.step === currentStep);

  return (
    <div className="space-y-4">
      <h3 className="font-bold text-sm">Install {extensionName}</h3>
      <div className="flex gap-1">
        {STEPS.map((s, i) => (
          <div key={s.step} className={`flex-1 h-1.5 rounded-full ${i <= stepIdx ? "bg-blue-500" : "bg-gray-200 dark:bg-gray-700"}`} />
        ))}
      </div>
      <div className="text-xs text-gray-500 text-center">{STEPS[stepIdx]?.label || currentStep}</div>

      {currentStep === "consent" && (
        <div className="space-y-2">
          <p className="text-sm">This extension requests the following permissions:</p>
          {permissions.map(p => (
            <label key={p} className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={granted.has(p)} onChange={() => {
                const next = new Set(granted);
                next.has(p) ? next.delete(p) : next.add(p);
                setGranted(next);
              }} />
              {p}
            </label>
          ))}
          <button onClick={() => onGrant?.([...granted])} className="w-full bg-blue-500 text-white py-2 rounded-lg text-sm">Grant & Continue</button>
        </div>
      )}
      {currentStep === "configure" && (
        <button onClick={() => onConfigure?.({})} className="w-full bg-blue-500 text-white py-2 rounded-lg text-sm">Use Defaults & Continue</button>
      )}
      {currentStep === "install" && (
        <button onClick={onComplete} className="w-full bg-green-500 text-white py-2 rounded-lg text-sm">Complete Installation</button>
      )}
      {currentStep === "complete" && (
        <div className="text-center py-4"><span className="text-3xl block">🎉</span><span className="font-bold mt-2 block">Installed Successfully!</span></div>
      )}
    </div>
  );
}
