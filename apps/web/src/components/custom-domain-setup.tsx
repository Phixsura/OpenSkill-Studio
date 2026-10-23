"use client";

interface DnsRecord { type: string; name: string; value: string; }
interface CustomDomainSetupProps { domain: string; dnsRecords: DnsRecord[]; sslStatus: string;
  verificationStatus: string; onVerify: () => void; }

const statusBadge = (s: string) => s === "active" || s === "verified"
  ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30";

export function CustomDomainSetup({ domain, dnsRecords, sslStatus, verificationStatus, onVerify }: CustomDomainSetupProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Custom Domain</h2>
      <div className="rounded-lg border p-4 dark:border-gray-700">
        <p className="font-mono text-sm font-bold">{domain}</p>
        <div className="mt-2 flex gap-2">
          <span className={`rounded-full px-2 py-0.5 text-xs ${statusBadge(sslStatus)}`}>SSL: {sslStatus}</span>
          <span className={`rounded-full px-2 py-0.5 text-xs ${statusBadge(verificationStatus)}`}>{verificationStatus}</span>
        </div>
      </div>
      <div>
        <h3 className="text-sm font-medium">DNS Records</h3>
        <div className="mt-2 space-y-1.5">
          {dnsRecords.map((r, i) => (
            <div key={i} className="flex gap-2 rounded border px-3 py-2 font-mono text-xs dark:border-gray-700">
              <span className="w-14 font-bold">{r.type}</span>
              <span className="text-gray-400">{r.name}</span>
              <span className="ml-auto">{r.value}</span>
            </div>
          ))}
        </div>
      </div>
      <button onClick={onVerify} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">
        Verify DNS
      </button>
    </div>
  );
}
