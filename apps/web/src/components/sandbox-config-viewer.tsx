"use client";

interface SandboxConfigViewerProps {
  runtime: string;
  memoryMb: number;
  timeoutSeconds: number;
  network?: { allowedHosts: string[]; egressPolicy: string };
}

export function SandboxConfigViewer({ runtime, memoryMb, timeoutSeconds, network }: SandboxConfigViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">⚙️ Sandbox Configuration</h4>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <span className="text-gray-500">Runtime</span>
          <p className="font-mono font-medium">{runtime}</p>
        </div>
        <div>
          <span className="text-gray-500">Memory</span>
          <p className="font-medium">{memoryMb} MB</p>
        </div>
        <div>
          <span className="text-gray-500">Timeout</span>
          <p className="font-medium">{timeoutSeconds}s</p>
        </div>
        <div>
          <span className="text-gray-500">Egress</span>
          <p className="font-medium capitalize">{network?.egressPolicy ?? "none"}</p>
        </div>
      </div>
      {network?.allowedHosts && network.allowedHosts.length > 0 && (
        <div className="mt-3">
          <span className="text-xs text-gray-500">Allowed Hosts</span>
          <div className="mt-1 flex flex-wrap gap-1">
            {network.allowedHosts.map(h => (
              <span key={h} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono dark:bg-gray-800">{h}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
