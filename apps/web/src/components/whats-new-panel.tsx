"use client";

interface WhatsNewItem { date: string; title: string; description: string; type: "feature" | "improvement" | "fix"; }

const typeConfig: Record<string, { icon: string; color: string }> = {
  feature: { icon: "✨", color: "text-green-600" },
  improvement: { icon: "📈", color: "text-blue-600" },
  fix: { icon: "🐛", color: "text-yellow-600" },
};

export function WhatsNewPanel({ items }: { items: WhatsNewItem[] }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🆕 What's New</h2>
      <div className="space-y-3">
        {items.map((item, i) => {
          const cfg = typeConfig[item.type];
          return (
            <div key={i} className="flex gap-3">
              <span className="text-xs text-gray-400 w-16 shrink-0 pt-0.5">{item.date}</span>
              <div>
                <div className="flex items-center gap-1">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{item.title}</span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
