"use client";

interface WorkspaceSettingsPanelProps { settings: Record<string, unknown>;
  customized: number; total: number; onUpdate: (key: string, value: unknown) => void;
  onReset: () => void; }

export function WorkspaceSettingsPanel({ settings, customized, total, onUpdate, onReset }: WorkspaceSettingsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Workspace Settings</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{customized}/{total} customized</span>
          <button onClick={onReset} className="text-xs text-red-500 hover:underline">Reset</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(settings).map(([key, value]) => (
          <div key={key} className="flex items-center justify-between px-4 py-2.5">
            <span className="text-sm font-mono">{key.replaceAll("_", " ")}</span>
            <span className="text-xs text-gray-400 font-mono">{String(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
