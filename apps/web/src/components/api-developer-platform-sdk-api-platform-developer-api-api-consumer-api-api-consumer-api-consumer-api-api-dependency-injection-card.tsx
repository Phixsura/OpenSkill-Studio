"use client";

interface Binding { id: string; interfaceName: string; implementation: string; scope: string; active: boolean; }
interface Props { bindings: Binding[]; consumerId: string; appName: string; }

const scopeColors: Record<string, string> = {
  singleton: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  transient: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  scoped: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiDependencyInjectionCard({ bindings, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💉 Service Bindings</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {bindings.length} bindings</p>
      </div>
      {bindings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No bindings</p>
      ) : (
        <div className="space-y-1">
          {bindings.map((b) => (
            <div key={b.id} className={`rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800 ${!b.active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <code className="text-blue-600 dark:text-blue-400">{b.interfaceName}</code>
                <span className={`rounded px-1 py-0.5 text-[9px] ${scopeColors[b.scope] ?? ""}`}>{b.scope}</span>
              </div>
              <div className="text-gray-400">→ {b.implementation}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
