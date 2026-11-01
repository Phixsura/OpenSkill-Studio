"use client";

interface TrustDetail { signal: string; weight: number; met: boolean; }
interface TrustScoreShieldProps { score: number; trustLevel: string; badge: string;
  details: TrustDetail[]; metCount: number; totalSignals: number; }

const levelColor: Record<string, string> = {
  high: "from-green-500 to-emerald-600",
  medium: "from-yellow-500 to-orange-500",
  low: "from-red-500 to-pink-600",
};
const signalLabels: Record<string, string> = {
  verified_developer: "Verified Developer", security_scan_clean: "Security Scan Clean",
  code_signed: "Code Signed", privacy_policy: "Privacy Policy",
  responsive_support: "Responsive Support", high_rating: "High Rating",
  active_maintenance: "Active Maintenance", open_source: "Open Source",
};

export function TrustScoreShield({ score, trustLevel, badge, details, metCount, totalSignals }: TrustScoreShieldProps) {
  return (
    <div className="space-y-4">
      <div className={`rounded-xl bg-gradient-to-r ${levelColor[trustLevel] ?? levelColor.medium} p-6 text-center text-white`}>
        <p className="text-4xl">🛡️</p>
        <p className="mt-2 text-3xl font-black">{score}/100</p>
        <p className="text-sm capitalize opacity-80">{trustLevel} Trust · {metCount}/{totalSignals}</p>
        {badge && <p className="mt-1 text-xs">{badge}</p>}
      </div>
      <div className="space-y-1.5">
        {details.map(d => (
          <div key={d.signal} className="flex items-center justify-between rounded border px-3 py-1.5 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{d.met ? "✅" : "⬜"}</span>
              <span className="text-sm">{signalLabels[d.signal] ?? d.signal}</span>
            </div>
            <span className="text-xs text-gray-400">+{d.weight}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
