"use client";

interface NetworkRule {
  domain: string;
  action: "allow" | "deny";
  protocols: string[];
}

interface FilesystemRule {
  path_prefix: string;
  readable: boolean;
  writable: boolean;
  max_file_bytes: number;
}

interface SandboxPolicyData {
  app_id: string;
  network_rules: NetworkRule[];
  filesystem_rules: FilesystemRule[];
  allowed_env_vars: string[];
  allowed_secret_keys: string[];
  max_execution_seconds: number;
  max_memory_mb: number;
  allow_subprocess: boolean;
  network_default: "allow" | "deny";
}

interface SandboxPolicyViewerProps {
  policy: SandboxPolicyData;
  appName: string;
  hasOrgOverride: boolean;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1048576).toFixed(0)} MB`;
}

function AllowDenyBadge({ allowed }: { allowed: boolean }) {
  return (
    <span
      className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${allowed ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"}`}
    >
      {allowed ? "Allow" : "Deny"}
    </span>
  );
}

function ChipList({ items, color }: { items: string[]; color: string }) {
  if (items.length === 0) return <span className="text-xs text-gray-400">None</span>;
  return (
    <div className="flex flex-wrap gap-1">
      {items.map((item) => (
        <code key={item} className={`rounded px-1.5 py-0.5 text-[10px] ${color}`}>
          {item}
        </code>
      ))}
    </div>
  );
}

export function SandboxPolicyViewer({ policy, appName, hasOrgOverride }: SandboxPolicyViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Sandbox Policy</h3>
          {hasOrgOverride && (
            <span className="rounded bg-purple-100 px-2 py-0.5 text-[10px] font-medium text-purple-700 dark:bg-purple-900/20 dark:text-purple-300">
              Org Override Active
            </span>
          )}
        </div>
        <p className="text-xs text-gray-500">{appName}</p>
      </div>

      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {/* Limits */}
        <div className="px-4 py-3">
          <p className="text-[10px] font-semibold uppercase text-gray-400">Resource Limits</p>
          <div className="mt-1.5 grid grid-cols-3 gap-2 text-xs">
            <div>
              <span className="text-gray-500">Timeout</span>
              <p className="font-medium">{policy.max_execution_seconds}s</p>
            </div>
            <div>
              <span className="text-gray-500">Memory</span>
              <p className="font-medium">{policy.max_memory_mb} MB</p>
            </div>
            <div>
              <span className="text-gray-500">Subprocess</span>
              <p>
                <AllowDenyBadge allowed={policy.allow_subprocess} />
              </p>
            </div>
          </div>
        </div>

        {/* Network */}
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-semibold uppercase text-gray-400">Network</p>
            <span className="text-[10px] text-gray-400">
              Default: {policy.network_default === "allow" ? "🟢 Allow" : "🔴 Deny"}
            </span>
          </div>
          {policy.network_rules.length === 0 ? (
            <p className="mt-1 text-xs text-gray-400">No rules — default applies</p>
          ) : (
            <ul className="mt-1.5 space-y-1">
              {policy.network_rules.map((r, i) => (
                <li key={i} className="flex items-center gap-2 text-xs">
                  <AllowDenyBadge allowed={r.action === "allow"} />
                  <code className="font-mono">{r.domain}</code>
                  <span className="text-gray-400">{r.protocols.join(", ")}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Filesystem */}
        <div className="px-4 py-3">
          <p className="text-[10px] font-semibold uppercase text-gray-400">Filesystem</p>
          {policy.filesystem_rules.length === 0 ? (
            <p className="mt-1 text-xs text-gray-400">No filesystem access</p>
          ) : (
            <ul className="mt-1.5 space-y-1">
              {policy.filesystem_rules.map((r, i) => (
                <li key={i} className="flex items-center gap-2 text-xs">
                  <code className="font-mono">{r.path_prefix}</code>
                  <span className={r.readable ? "text-green-600" : "text-red-600"}>
                    R{r.readable ? "✓" : "✗"}
                  </span>
                  <span className={r.writable ? "text-green-600" : "text-red-600"}>
                    W{r.writable ? "✓" : "✗"}
                  </span>
                  <span className="text-gray-400">max {formatBytes(r.max_file_bytes)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Env vars */}
        <div className="px-4 py-3">
          <p className="text-[10px] font-semibold uppercase text-gray-400">Environment Variables</p>
          <div className="mt-1.5">
            <ChipList
              items={policy.allowed_env_vars}
              color="bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
            />
          </div>
        </div>

        {/* Secrets */}
        <div className="px-4 py-3">
          <p className="text-[10px] font-semibold uppercase text-gray-400">Secret Keys</p>
          <div className="mt-1.5">
            <ChipList
              items={policy.allowed_secret_keys}
              color="bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
