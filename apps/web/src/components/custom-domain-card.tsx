"use client";

interface DomainInfo {
  domain_id: string;
  domain: string;
  status: "pending" | "verifying" | "verified" | "failed";
  ssl_status: "none" | "provisioning" | "active" | "expired";
}

interface CustomDomainCardProps {
  domains: DomainInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  pending: { icon: "⏳", text: "text-gray-500" },
  verifying: { icon: "🔍", text: "text-blue-600 dark:text-blue-400" },
  verified: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  failed: { icon: "❌", text: "text-red-500" },
};

const SSL_STYLES: Record<string, { label: string; color: string }> = {
  none: { label: "No SSL", color: "text-gray-400" },
  provisioning: { label: "SSL provisioning", color: "text-blue-500" },
  active: { label: "SSL active", color: "text-green-600 dark:text-green-400" },
  expired: { label: "SSL expired", color: "text-red-500" },
};

export default function CustomDomainCard({ domains, appName }: CustomDomainCardProps) {
  const verifiedCount = domains.filter((d) => d.status === "verified").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Custom Domains</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {verifiedCount}/{domains.length} verified
        </span>
      </div>

      {domains.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom domains</p>
      ) : (
        <div className="space-y-2">
          {domains.map((d) => {
            const st = STATUS_STYLES[d.status] ?? STATUS_STYLES.pending;
            const ssl = SSL_STYLES[d.ssl_status] ?? SSL_STYLES.none;
            return (
              <div
                key={d.domain_id}
                className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
              >
                <div className="flex items-center gap-2">
                  <span>{st.icon}</span>
                  <div>
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                      {d.domain}
                    </span>
                    <p className={`text-[11px] ${ssl.color}`}>{ssl.label}</p>
                  </div>
                </div>
                <span className={`text-xs font-medium capitalize ${st.text}`}>{d.status}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
