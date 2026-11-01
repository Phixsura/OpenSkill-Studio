"use client";

interface ChainInfo { chain: string[]; depth: number; }
interface DepChainViewerProps { chains: Record<string, ChainInfo>; maxDepth: number;
  criticalPaths: string[]; serviceCount: number; }

export function DepChainViewer({ chains, maxDepth, criticalPaths, serviceCount }: DepChainViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Dependency Chains</h3>
        <span className="text-xs text-gray-400">{serviceCount} services · max depth {maxDepth}{criticalPaths.length > 0 ? ` · ⚠ ${criticalPaths.length} critical` : ""}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(chains).map(([svc, info]) => (
          <div key={svc} className="px-4 py-1.5 text-xs">
            <span className={`font-mono ${info.depth >= 3 ? "text-red-600 font-bold" : ""}`}>
              {info.chain.join(" → ")}
            </span>
            <span className="text-gray-400 ml-2">(depth {info.depth})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
