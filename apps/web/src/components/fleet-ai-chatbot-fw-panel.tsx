"use client";
export function FleetAiChatbotFwPanel({ bots, active, conversations, csat, containment }: { bots: number; active: number; conversations: number; csat: number; containment: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💬 AI Chatbot Framework</h3>
    <div className="text-sm">{active}/{bots} active · {conversations.toLocaleString()} convos · CSAT {csat} · {containment}% contained</div>
  </div>);
}
