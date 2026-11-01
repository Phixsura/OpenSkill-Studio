"use client";

interface AIModel { modelId: string; provider: string; name: string; maxTokens: number; costPer1kInput: number; costPer1kOutput: number; }
interface AIUsage { modelId: string; requests: number; inputTokens: number; outputTokens: number; totalCostCents: number; cachedResponses: number; }

const providerIcons: Record<string, string> = { anthropic: "🤖", openai: "🧠", local: "💻" };

export function AIIntegrationPanel({ models, usage, totalCostCents }: {
  models: AIModel[]; usage: AIUsage[]; totalCostCents: number;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🤖 AI Integration</h2>
        <span className="text-sm font-bold text-blue-600">${(totalCostCents / 100).toFixed(2)} total</span>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {models.map((m) => (
          <div key={m.modelId} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <span className="text-xl block">{providerIcons[m.provider] || "🤖"}</span>
            <span className="font-semibold text-xs block mt-1">{m.name}</span>
            <span className="text-[10px] text-gray-400">${m.costPer1kInput}¢/1K in · ${m.costPer1kOutput}¢/1K out</span>
          </div>
        ))}
      </div>

      {usage.length > 0 && (
        <div className="space-y-1">
          <span className="text-sm font-semibold">Usage</span>
          {usage.map((u) => (
            <div key={u.modelId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-sm">
              <code className="text-xs">{u.modelId}</code>
              <div className="flex gap-3 text-xs text-gray-500">
                <span>{u.requests} reqs</span>
                <span>{(u.inputTokens / 1000).toFixed(1)}K in</span>
                <span>{(u.outputTokens / 1000).toFixed(1)}K out</span>
                <span className="text-blue-600">${(u.totalCostCents / 100).toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
