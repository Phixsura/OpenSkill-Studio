"use client";

interface CollectionCardProps {
  title: string;
  description: string;
  appCount: number;
  previewApps: { name: string; icon?: string }[];
  slug: string;
}

export function CollectionCard({ title, description, appCount, previewApps, slug }: CollectionCardProps) {
  return (
    <a href={`/marketplace/collections/${slug}`}
      className="block rounded-lg border border-gray-200 p-4 transition hover:shadow-md dark:border-gray-700">
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-gray-500 line-clamp-2">{description}</p>
      <div className="mt-3 flex items-center gap-2">
        {previewApps.map((a, i) => (
          <span key={i} className="flex h-8 w-8 items-center justify-center rounded-md bg-gray-100 text-sm dark:bg-gray-700">
            {a.icon || a.name[0]}
          </span>
        ))}
        {appCount > previewApps.length && (
          <span className="text-xs text-gray-400">+{appCount - previewApps.length}</span>
        )}
      </div>
      <p className="mt-2 text-xs text-gray-400">{appCount} apps</p>
    </a>
  );
}
