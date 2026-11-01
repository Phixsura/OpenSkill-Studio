"use client";

interface CollectionCardProps { title: string; description: string; curator: string;
  appCount: number; featured: boolean; onClick: () => void; }

export function CollectionCard({ title, description, curator, appCount, featured, onClick }: CollectionCardProps) {
  return (
    <button onClick={onClick}
      className={`w-full rounded-xl border p-4 text-left hover:shadow transition ${featured ? "border-yellow-400 bg-yellow-50 dark:bg-yellow-900/10" : "dark:border-gray-700"}`}>
      {featured && <span className="mb-1 inline-block text-xs text-yellow-600">⭐ Featured Collection</span>}
      <h3 className="text-sm font-bold">{title}</h3>
      <p className="mt-1 text-xs text-gray-500 line-clamp-2">{description}</p>
      <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
        <span>by {curator}</span>
        <span>{appCount} apps</span>
      </div>
    </button>
  );
}
