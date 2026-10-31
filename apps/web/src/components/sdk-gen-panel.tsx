"use client";
interface SdkMethod { name: string; httpMethod: string; path: string; }
interface SdkGenPanelProps { sdkName: string; version: string; methods: SdkMethod[];
  totalMethods: number; coveragePct: number; }
const METHOD_COLOR: Record<string, string> = { GET: "text-green-600", POST: "text-blue-500", PUT: "text-yellow-600", DELETE: "text-red-500" };
export function SdkGenPanel({ sdkName, version, methods, totalMethods, coveragePct }: SdkGenPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 SDK: {sdkName} v{version}</h3>
        <span className="text-xs text-gray-400">{totalMethods} methods · {coveragePct}% coverage</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {methods.map(m => (
          <div key={m.name} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{m.name}()</span>
            <span className="text-gray-400"><span className={METHOD_COLOR[m.httpMethod] ?? ""}>{m.httpMethod}</span> {m.path}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
