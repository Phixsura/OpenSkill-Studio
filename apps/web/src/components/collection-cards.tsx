"use client";

interface Collection { title: string; description: string; appCount: number;
  curator: string; featured: boolean; }
interface CollectionCardsProps { collections: Collection[];
  onSelect: (title: string) => void; }

export function CollectionCards({ collections, onSelect }: CollectionCardsProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {collections.map(c => (
        <button key={c.title} onClick={() => onSelect(c.title)}
          className={`rounded-xl border p-5 text-left hover:shadow-lg transition ${
            c.featured ? "border-yellow-300 dark:border-yellow-700" : "dark:border-gray-700"
          }`}>
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-bold">{c.title}</h4>
            {c.featured && <span className="text-xs text-yellow-500">⭐ Featured</span>}
          </div>
          <p className="text-xs text-gray-500 mb-2">{c.description}</p>
          <div className="flex gap-3 text-xs text-gray-400">
            <span>📱 {c.appCount} apps</span>
            <span>By {c.curator}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
