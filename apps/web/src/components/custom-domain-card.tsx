"use client";

interface CustomDomainInfo {
  domain_id: string;
  hostname: string;
  target: string;
  dns_status: "pending" | "verified" | "failed";
  ssl_status: "none" | "provisioning" | "active" | "expired";
  is_ready: boolean;
}

interface CustomDomainCardProps {
  domains: CustomDomainInfo[];
  appName: string;
}

const dnsStyle: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  verified: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

const sslStyle: Record<string, string> = {
  none: "text-gray-400",
  provisioning: "text-yellow-500",
  active: "text-green-500",
  expired: "text-red-500",
};

export default function CustomDomainCard({ domains, appName }: CustomDomainCardProps) {
  const ready = domains.filter((d) => d.is_ready).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🌐 Custom Domains
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {ready}/{domains.length} ready
        </span>
      </div>

      {domains.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom domains</p>
      ) : (
        <div className="space-y-2">
          {domains.map((d) => (
            <div
              key={d.domain_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {d.hostname}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${dnsStyle[d.dns_status] ?? ""}`}
                >
                  DNS {d.dns_status}
                </span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                <span>→ {d.target}</span>
                <span className={sslStyle[d.ssl_status] ?? ""}>SSL {d.ssl_status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
