"use client";

interface ProviderConfig {
  provider: string;
  headerName: string;
  configured: boolean;
}

export function WebhookSigPanel({
  providers,
  onConfigure,
  onTest,
}: {
  providers: ProviderConfig[];
  onConfigure?: (provider: string) => void;
  onTest?: (provider: string) => void;
}) {
  const providerIcons: Record<string, string> = {
    github: "🐙", stripe: "💳", slack: "💬", custom: "🔧",
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔏 Webhook Signatures</h2>
      <div className="space-y-1">
        {providers.map((p) => (
          <div key={p.provider} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>{providerIcons[p.provider] || "🔑"}</span>
              <span className="font-semibold text-sm capitalize">{p.provider}</span>
              <code className="text-xs text-gray-400">{p.headerName}</code>
              <span className={`w-2 h-2 rounded-full ${p.configured ? "bg-green-500" : "bg-gray-300"}`} />
            </div>
            <div className="flex gap-1">
              <button onClick={() => onTest?.(p.provider)}
                className="text-xs bg-blue-600 text-white px-2 py-1 rounded" disabled={!p.configured}>Test</button>
              <button onClick={() => onConfigure?.(p.provider)}
                className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {p.configured ? "Update" : "Configure"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
