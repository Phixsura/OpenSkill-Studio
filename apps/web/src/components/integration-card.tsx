"use client";

interface IntegrationCardProps { id: string; label: string; icon: string; category: string;
  connected: boolean; cta: string; onAction: () => void; }

export function IntegrationCard({ id, label, icon, category, connected, cta, onAction }: IntegrationCardProps) {
  return (
    <div className={`rounded-xl border p-4 ${connected ? "border-green-300 dark:border-green-700" : "dark:border-gray-700"}`}>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div className="flex-1">
          <p className="text-sm font-semibold">{label}</p>
          <p className="text-xs text-gray-400">{category}</p>
        </div>
        {connected && <span className="h-2.5 w-2.5 rounded-full bg-green-500" />}
      </div>
      <button onClick={onAction}
        className={`mt-3 w-full rounded-lg py-1.5 text-sm font-medium ${connected ? "border text-red-600 dark:border-gray-700" : "bg-blue-600 text-white"}`}>
        {cta}
      </button>
    </div>
  );
}
