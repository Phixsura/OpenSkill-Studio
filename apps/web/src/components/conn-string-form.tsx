"use client";

interface ConnStringFormProps { uri: string; masked: string; engine: string;
  engines: string[]; onBuild: (engine: string) => void; }

const ENGINE_ICONS: Record<string, string> = {
  postgres: "🐘", mysql: "🐬", mongodb: "🍃", redis: "🔴",
};

export function ConnStringForm({ uri, masked, engine, engines, onBuild }: ConnStringFormProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Connection String</h3>
      </div>
      <div className="p-4 space-y-3">
        <div className="flex gap-2">
          {engines.map(e => (
            <button key={e} onClick={() => onBuild(e)}
              className={`px-3 py-1 text-xs rounded-lg ${e === engine ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
              {ENGINE_ICONS[e] ?? "💾"} {e}
            </button>
          ))}
        </div>
        {masked && (
          <div className="p-3 bg-gray-900 text-gray-200 rounded-lg font-mono text-xs break-all">
            {masked}
          </div>
        )}
      </div>
    </div>
  );
}
