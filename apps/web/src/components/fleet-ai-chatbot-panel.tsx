"use client";
export function FleetAiChatbotPanel({ bots, active, conversations, satisfaction }: { bots: number; active: number; conversations: number; satisfaction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💬 AI Chatbot</h3>
    <div className="text-sm">{active}/{bots} active · {conversations.toLocaleString()} conversations · {satisfaction}% satisfaction</div>
  </div>);
}
