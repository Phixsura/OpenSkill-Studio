"use client";

interface Signal { type: string; icon: string; text: string; }
interface SocialProofBadgesProps { signals: Signal[]; trustScore: number; }

export function SocialProofBadges({ signals, trustScore }: SocialProofBadgesProps) {
  if (signals.length === 0) return null;
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {signals.map(s => (
          <span key={s.type} className="flex items-center gap-1 rounded-full border border-gray-200 bg-white px-3 py-1 text-xs shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <span>{s.icon}</span>
            <span>{s.text}</span>
          </span>
        ))}
      </div>
      {trustScore >= 60 && (
        <p className="text-xs text-green-600">🛡️ High trust score ({trustScore}/100)</p>
      )}
    </div>
  );
}
