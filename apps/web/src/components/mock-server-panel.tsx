"use client";

interface MockEndpoint { path: string; method: string; status_code: number; }
interface MockServerPanelProps { endpoints: MockEndpoint[]; port: number; isRunning: boolean; onToggle: () => void; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-700", POST: "bg-blue-100 text-blue-700",
  PUT: "bg-yellow-100 text-yellow-700", DELETE: "bg-red-100 text-red-700",
};

export function MockServerPanel({ endpoints, port, isRunning, onToggle }: MockServerPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Mock Server</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${isRunning ? "bg-green-500" : "bg-gray-300"}`} />
          <span className="text-xs text-gray-400">:{port}</span>
          <button onClick={onToggle} className={`rounded px-2 py-1 text-xs ${isRunning ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`}>
            {isRunning ? "Stop" : "Start"}
          </button>
        </div>
      </div>
      <ul className="mt-3 space-y-1">
        {endpoints.map((e, i) => (
          <li key={i} className="flex items-center gap-2 text-sm">
            <span className={`rounded px-1.5 py-0.5 text-xs font-mono ${METHOD_COLORS[e.method] || "bg-gray-100"}`}>{e.method}</span>
            <code className="text-xs flex-1">{e.path}</code>
            <span className="text-xs text-gray-400">{e.status_code}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
