"use client";
export function FleetAiConvMemPanel({ stores, active, conversations, messages, avgContext }: { stores: number; active: number; conversations: number; messages: number; avgContext: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 AI Conversation Memory</h3>
    <div className="text-sm">{active}/{stores} active · {conversations.toLocaleString()} convos · {messages.toLocaleString()} msgs · {avgContext.toLocaleString()} ctx</div>
  </div>);
}
