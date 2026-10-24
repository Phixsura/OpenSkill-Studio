"use client";
export function FleetAiConvMemPanel({ stores, active, conversations, messages }: { stores: number; active: number; conversations: number; messages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💭 Conv Memory</h3>
    <div className="text-sm">{active}/{stores} active · {conversations.toLocaleString()} convs · {messages.toLocaleString()} msgs</div>
  </div>);
}
