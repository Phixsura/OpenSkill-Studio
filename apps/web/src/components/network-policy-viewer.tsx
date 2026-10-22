"use client";

interface NetworkPolicyViewerProps {
  allowedHosts: string[]; blockedPorts: number[];
  maxConnections: number; bandwidthLimitMbps: number;
}

export function NetworkPolicyViewer({ allowedHosts, blockedPorts, maxConnections, bandwidthLimitMbps }: NetworkPolicyViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Network Policy</h3>
      <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-xs font-medium text-gray-500">Allowed Hosts</p>
          {allowedHosts.length === 0 ? <p className="text-xs text-gray-400">None configured</p> :
            <ul className="mt-1 space-y-0.5">{allowedHosts.map(h => <li key={h} className="font-mono text-xs">{h}</li>)}</ul>}
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500">Blocked Ports</p>
          <p className="mt-1 font-mono text-xs text-gray-600 dark:text-gray-400">{blockedPorts.join(", ")}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500">Max Connections</p>
          <p className="mt-1 text-lg font-bold">{maxConnections}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500">Bandwidth Limit</p>
          <p className="mt-1 text-lg font-bold">{bandwidthLimitMbps} Mbps</p>
        </div>
      </div>
    </div>
  );
}
