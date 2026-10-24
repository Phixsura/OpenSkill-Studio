"use client";

interface ToggleRouterPanelProps { flags: Record<string, boolean>; enabledCount: number;
  totalFlags: number; userId: string; }

export function ToggleRouterPanel({ flags, enabledCount, totalFlags, userId }: ToggleRouterPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚩 Feature Toggles</h3>
        <span className="text-xs text-gray-400">{enabledCount}/{totalFlags} on · {userId}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(flags).map(([flag, on]) => (
          <div key={flag} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{flag}</span>
            <span className={on ? "text-green-600" : "text-gray-400"}>{on ? "● ON" : "○ OFF"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
