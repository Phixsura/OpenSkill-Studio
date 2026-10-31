"use client";

import { useState } from "react";

interface ActivityItem {
  id: string;
  type: "install" | "publish" | "review" | "update" | "uninstall" | "incident";
  actor: string;
  target: string;
  message: string;
  timestamp: string;
}

const typeConfig: Record<string, { icon: string; color: string }> = {
  install: { icon: "⬇️", color: "text-green-500" },
  publish: { icon: "🚀", color: "text-blue-500" },
  review: { icon: "⭐", color: "text-yellow-500" },
  update: { icon: "🔄", color: "text-purple-500" },
  uninstall: { icon: "🗑️", color: "text-gray-400" },
  incident: { icon: "🚨", color: "text-red-500" },
};

export function MarketplaceActivityFeed({
  activities,
  onLoadMore,
  hasMore,
}: {
  activities: ActivityItem[];
  onLoadMore?: () => void;
  hasMore?: boolean;
}) {
  const [filter, setFilter] = useState<string>("all");
  const types = ["all", ...Object.keys(typeConfig)];
  const filtered = filter === "all" ? activities : activities.filter((a) => a.type === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📰 Activity Feed</h2>
        <span className="text-sm text-gray-400">{filtered.length} events</span>
      </div>

      <div className="flex gap-1 overflow-x-auto">
        {types.map((t) => (
          <button key={t} onClick={() => setFilter(t)}
            className={`text-xs px-2.5 py-1 rounded-full whitespace-nowrap ${
              filter === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"
            }`}>{t}</button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((item) => {
          const cfg = typeConfig[item.type];
          return (
            <div key={item.id} className="flex items-start gap-3 py-2 border-b dark:border-gray-800 last:border-0">
              <span className={`text-lg mt-0.5 ${cfg.color}`}>{cfg.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm">
                  <span className="font-medium">{item.actor}</span>
                  {" "}<span className="text-gray-500">{item.message}</span>{" "}
                  <span className="font-medium">{item.target}</span>
                </div>
              </div>
              <span className="text-xs text-gray-400 shrink-0">{item.timestamp}</span>
            </div>
          );
        })}
        {filtered.length === 0 && <div className="text-center text-gray-400 py-4 text-sm">No activity</div>}
      </div>

      {hasMore && onLoadMore && (
        <button onClick={onLoadMore} className="w-full text-center text-sm text-blue-500 py-2">Load more...</button>
      )}
    </div>
  );
}
