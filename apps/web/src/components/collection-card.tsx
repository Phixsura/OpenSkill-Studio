"use client";

interface CollectionCardProps { title: string; description: string; appCount: number; slug: string; }

export function CollectionCard({ title, description, appCount, slug }: CollectionCardProps) {
  return (
    <a href={`/marketplace/collections/${slug}`} className="block rounded-xl border border-gray-200 p-5 transition-colors hover:border-blue-400 dark:border-gray-700">
      <h4 className="text-lg font-semibold">{title}</h4>
      <p className="mt-1 text-sm text-gray-500 line-clamp-2">{description}</p>
      <p className="mt-2 text-xs text-gray-400">📦 {appCount} apps</p>
    </a>
  );
}
