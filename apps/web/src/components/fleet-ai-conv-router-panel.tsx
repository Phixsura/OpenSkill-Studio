"use client";
export function FleetAiConvRouterPanel({ routers, active, conversations, models, optimalPct }: { routers: number; active: number; conversations: number; models: number; optimalPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Conversation Router</h3>
    <div className="text-sm">{active}/{routers} active · {conversations.toLocaleString()} convos · {models} models · {optimalPct}% optimal</div>
  </div>);
}
