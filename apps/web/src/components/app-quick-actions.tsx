"use client";

interface QuickAction { label: string; icon: string; href: string; description: string; }

interface AppQuickActionsProps {
  actions: QuickAction[];
}

export function AppQuickActions({ actions }: AppQuickActionsProps) {
  if (actions.length === 0) return null;
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {actions.map(a => (
        <a key={a.label} href={a.href}
          className="rounded-lg border border-gray-200 p-3 text-center transition-colors hover:border-blue-400 dark:border-gray-700">
          <span className="text-2xl">{a.icon}</span>
          <p className="mt-1 text-sm font-medium">{a.label}</p>
          <p className="text-xs text-gray-500">{a.description}</p>
        </a>
      ))}
    </div>
  );
}
