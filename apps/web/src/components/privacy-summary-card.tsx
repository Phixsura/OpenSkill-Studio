"use client";

interface DataItem { id: string; icon: string; label: string; risk: string; }
interface PrivacySummaryCardProps { appName: string; dataCollected: DataItem[];
  maxRisk: string; hasPrivacyPolicy: boolean; privacyUrl: string; }

const RISK_COLOR: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-orange-600", critical: "text-red-600",
};

function getSafeUrl(url: string): string | null {
  try {
    const u = new URL(url);
    return ["http:", "https:"].includes(u.protocol) ? u.href : null;
  } catch {
    return null;
  }
}

export function PrivacySummaryCard({ appName, dataCollected, maxRisk, hasPrivacyPolicy, privacyUrl }: PrivacySummaryCardProps) {
  const safeUrl = getSafeUrl(privacyUrl);
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔒 Data Privacy</h3>
        <span className={`text-xs font-medium capitalize ${RISK_COLOR[maxRisk] || ""}`}>
          {maxRisk} risk
        </span>
      </div>
      <div className="space-y-1.5 mb-3">
        {dataCollected.map(d => (
          <div key={d.id} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
            <span>{d.icon} {d.label}</span>
            <span className={`text-xs ${RISK_COLOR[d.risk] || ""}`}>{d.risk}</span>
          </div>
        ))}
        {dataCollected.length === 0 && <p className="text-sm text-gray-400">No data collection declared</p>}
      </div>
      {safeUrl ? (
        <a href={safeUrl} target="_blank" rel="noopener noreferrer"
          className="text-xs text-blue-600 hover:text-blue-700">📄 View Privacy Policy →</a>
      ) : hasPrivacyPolicy ? (
        <p className="text-xs text-gray-400">Privacy policy link unavailable</p>
      ) : (
        <p className="text-xs text-red-500">⚠️ No privacy policy provided</p>
      )}
    </div>
  );
}
