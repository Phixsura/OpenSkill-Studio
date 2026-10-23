"use client";

interface DigestItem { title: string; body: string; priority: string; }
interface DigestSection { category: string; count: number; items: DigestItem[]; }
interface NotifDigestCardProps { period: string; total: number; highPriority: number;
  sections: DigestSection[]; summary: string; }

const CAT_ICON: Record<string, string> = { alerts: "🚨", deploys: "🚀", reviews: "👀", general: "📌" };

export function NotifDigestCard({ period, total, highPriority, sections, summary }: NotifDigestCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold">📬 {period.charAt(0).toUpperCase() + period.slice(1)} Digest</h3>
          <p className="text-xs text-gray-400">{summary}</p>
        </div>
        {highPriority > 0 && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">{highPriority} urgent</span>}
      </div>
      {sections.map(s => (
        <div key={s.category} className="border-b last:border-0 dark:border-gray-700">
          <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 text-xs font-semibold text-gray-400">
            {CAT_ICON[s.category] || "📌"} {s.category} ({s.count})
          </div>
          {s.items.map((item, i) => (
            <div key={i} className="px-4 py-2 text-sm flex justify-between">
              <div>
                <span className={`font-medium ${item.priority === "high" ? "text-red-600" : ""}`}>{item.title}</span>
                <span className="text-xs text-gray-400 ml-2">{item.body}</span>
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
