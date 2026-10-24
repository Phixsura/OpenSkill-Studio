"use client";
export function FleetAutogenPanel({ groups, active, conversations, agents }: { groups: number; active: number; conversations: number; agents: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 AutoGen</h3>
    <div className="text-sm">{active}/{groups} active · {agents} agents · {conversations.toLocaleString()} conversations</div>
  </div>);
}
