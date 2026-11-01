"use client";

interface DnsRecord { type: string; name: string; value: string; ttl: number; }
interface CustomDomainSetupProps {
  domain: string; status: string; dnsRecords: DnsRecord[];
  verificationToken: string; verified: boolean;
}

export function CustomDomainSetup({ domain, status, dnsRecords, verificationToken, verified }: CustomDomainSetupProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🌐 Custom Domain</h3>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          verified ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
        }`}>{status}</span>
      </div>
      <div className="mb-4">
        <p className="text-sm font-medium">{domain}</p>
      </div>
      <div className="mb-4">
        <h4 className="text-xs font-semibold text-gray-400 mb-2 uppercase">DNS Records</h4>
        <div className="space-y-2">
          {dnsRecords.map((r, i) => (
            <div key={i} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-xs font-mono">
              <span className="text-blue-600 dark:text-blue-400">{r.type}</span>
              <span className="text-gray-400 mx-2">{r.name}</span>
              <span className="text-green-600 dark:text-green-400">{r.value}</span>
            </div>
          ))}
        </div>
      </div>
      {!verified && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 text-xs">
          <p className="font-medium text-yellow-700 dark:text-yellow-400 mb-1">Verification Required</p>
          <p className="text-yellow-600 dark:text-yellow-300">Add TXT record: <code>{verificationToken}</code></p>
        </div>
      )}
    </div>
  );
}
