"use client";

interface FeedItem { title: string; link: string; description: string; pubDate: string; category: string; }
interface RssFeedViewerProps { title: string; items: FeedItem[]; itemCount: number; }

const CAT_BADGE: Record<string, string> = {
  release: "bg-green-100 text-green-700", announcement: "bg-blue-100 text-blue-700",
  blog: "bg-purple-100 text-purple-700",
};

export function RssFeedViewer({ title, items, itemCount }: RssFeedViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 {title}</h3>
        <span className="text-xs text-gray-400">{itemCount} items</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {items.map((item, i) => (
          <div key={i} className="px-4 py-3">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium">{item.title}</span>
              {item.category && (
                <span className={`text-xs px-1.5 py-0.5 rounded ${CAT_BADGE[item.category] || "bg-gray-100"}`}>{item.category}</span>
              )}
            </div>
            {item.description && <p className="text-xs text-gray-400 line-clamp-2">{item.description}</p>}
            <p className="text-xs text-gray-300 mt-0.5">{item.pubDate}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
