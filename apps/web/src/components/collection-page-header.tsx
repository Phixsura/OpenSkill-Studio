"use client";

interface CollectionPageHeaderProps { title: string; description: string; appCount: number; collectionType: string; curatorName?: string; }

const TYPE_BADGES: Record<string, { label: string; color: string }> = {
  editorial: { label: "Editorial Pick", color: "bg-purple-100 text-purple-700" },
  trending: { label: "Trending", color: "bg-orange-100 text-orange-700" },
  category_best: { label: "Category Best", color: "bg-blue-100 text-blue-700" },
  new_arrivals: { label: "New Arrivals", color: "bg-green-100 text-green-700" },
  manual: { label: "Curated", color: "bg-gray-100 text-gray-700" },
};

export function CollectionPageHeader({ title, description, appCount, collectionType, curatorName }: CollectionPageHeaderProps) {
  const badge = TYPE_BADGES[collectionType] || TYPE_BADGES.manual;
  return (
    <div className="rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 p-6 dark:from-blue-900/10 dark:to-purple-900/10">
      <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${badge.color}`}>{badge.label}</span>
      <h1 className="mt-3 text-2xl font-bold">{title}</h1>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
      <div className="mt-3 flex items-center gap-3 text-xs text-gray-400">
        <span>📦 {appCount} apps</span>
        {curatorName && <span>👤 Curated by {curatorName}</span>}
      </div>
    </div>
  );
}
