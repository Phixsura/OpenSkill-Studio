"use client";

interface QuickAction { label: string; icon: string; href: string; }

interface DeveloperPortalLayoutProps {
  developerName: string; isNew: boolean; appCount: number; quickActions: QuickAction[];
  children: React.ReactNode;
}

export function DeveloperPortalLayout({ developerName, isNew, appCount, quickActions, children }: DeveloperPortalLayoutProps) {
  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-6 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
        <h1 className="text-2xl font-bold">{isNew ? `Welcome, ${developerName}! 👋` : `Welcome back, ${developerName}`}</h1>
        <p className="mt-1 opacity-80">{isNew ? "Start building on OpenSkill" : `${appCount} app${appCount !== 1 ? "s" : ""}`}</p>
      </div>
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {quickActions.map(a => (
          <a key={a.label} href={a.href} className="rounded-lg border border-gray-200 p-3 text-center transition hover:border-blue-400 dark:border-gray-700">
            <span className="text-xl">{a.icon}</span>
            <p className="mt-1 text-sm font-medium">{a.label}</p>
          </a>
        ))}
      </div>
      {children}
    </div>
  );
}
