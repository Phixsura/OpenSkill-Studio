"use client";

interface DigestItem { title: string; description: string; }
interface DigestSection { type: string; count: number; items: DigestItem[]; hasMore: boolean; }
interface DigestEmailProps { subject: string; period: string; sections: DigestSection[]; totalEvents: number; }

const typeIcons: Record<string, string> = {
  install: "📦", review: "⭐", update: "🔄", deploy: "🚀", comment: "💬",
};

export function DigestEmail({ subject, period, sections, totalEvents }: DigestEmailProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h2 className="text-lg font-bold">{subject}</h2>
      <p className="text-xs text-gray-400 mt-1 capitalize">{period} digest · {totalEvents} events</p>
      <div className="mt-4 space-y-4">
        {sections.map(s => (
          <div key={s.type}>
            <div className="flex items-center gap-2 mb-2">
              <span>{typeIcons[s.type] ?? "📌"}</span>
              <h3 className="text-sm font-semibold capitalize">{s.type} ({s.count})</h3>
            </div>
            <ul className="space-y-1 pl-6">
              {s.items.map((item, i) => (
                <li key={i} className="text-sm">{item.title}
                  {item.description && <span className="text-gray-400"> — {item.description}</span>}
                </li>
              ))}
              {s.hasMore && <li className="text-xs text-blue-600">+ {s.count - s.items.length} more</li>}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
