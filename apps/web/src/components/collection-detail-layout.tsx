"use client";

interface CollectionDetailLayoutProps {
  title: string; description: string; type: string; appCount: number;
  curatorName: string; curatorVerified: boolean; children: React.ReactNode;
}

const TYPE_LABELS: Record<string, { label: string; color: string }> = {
  editorial: { label: "Editorial Pick", color: "bg-purple-100 text-purple-700" },
  trending: { label: "Trending", color: "bg-orange-100 text-orange-700" },
  manual: { label: "Curated", color: "bg-blue-100 text-blue-700" },
};

export function CollectionDetailLayout({ title, description, type, appCount, curatorName, curatorVerified, children }: CollectionDetailLayoutProps) {
  const badge = TYPE_LABELS[type] || TYPE_LABELS.manual;
  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-gradient-to-r from-purple-50 to-blue-50 p-6 dark:from-purple-900/10 dark:to-blue-900/10">
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${badge.color}`}>{badge.label}</span>
        <h1 className="mt-2 text-2xl font-bold">{title}</h1>
        <p className="mt-1 text-sm text-gray-500">{description}</p>
        <div className="mt-2 flex gap-3 text-xs text-gray-400">
          <span>📦 {appCount} apps</span>
          <span>👤 {curatorName} {curatorVerified && "✅"}</span>
        </div>
      </div>
      <div>{children}</div>
    </div>
  );
}
