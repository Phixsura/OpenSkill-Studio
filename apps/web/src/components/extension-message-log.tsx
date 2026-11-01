"use client";

interface Message { type: string; direction: "in" | "out"; timestamp: string; payload?: Record<string, unknown>; }

interface ExtensionMessageLogProps { messages: Message[]; }

export function ExtensionMessageLog({ messages }: ExtensionMessageLogProps) {
  if (messages.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No messages</p>;
  return (
    <div className="max-h-60 space-y-1 overflow-y-auto font-mono text-xs">
      {messages.map((m, i) => (
        <div key={i} className={`rounded p-1 ${m.direction === "in" ? "bg-blue-50 dark:bg-blue-900/20" : "bg-green-50 dark:bg-green-900/20"}`}>
          <span className="text-gray-400">{m.timestamp}</span>
          <span className={`ml-1 ${m.direction === "in" ? "text-blue-600" : "text-green-600"}`}>{m.direction === "in" ? "←" : "→"}</span>
          <span className="ml-1 font-semibold">{m.type}</span>
        </div>
      ))}
    </div>
  );
}
