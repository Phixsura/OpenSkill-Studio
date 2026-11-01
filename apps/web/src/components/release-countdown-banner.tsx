"use client";

interface ReleaseCountdownBannerProps { appName: string; version: string; daysRemaining: number;
  hoursRemaining: number; isReleased: boolean; features: string[]; featureCount: number; }

export function ReleaseCountdownBanner({ appName, version, daysRemaining, hoursRemaining,
  isReleased, features, featureCount }: ReleaseCountdownBannerProps) {
  if (isReleased) {
    return (
      <div className="rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 p-6 text-center text-white">
        <p className="text-3xl">🎉</p>
        <h2 className="mt-2 text-xl font-black">{appName} v{version} is Live!</h2>
      </div>
    );
  }
  return (
    <div className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 p-6 text-white">
      <p className="text-center text-xs opacity-60">Coming Soon</p>
      <h2 className="mt-1 text-center text-xl font-black">{appName} v{version}</h2>
      <div className="mt-4 flex justify-center gap-4">
        <div className="text-center">
          <p className="text-3xl font-black">{daysRemaining}</p>
          <p className="text-xs opacity-60">Days</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-black">{hoursRemaining}</p>
          <p className="text-xs opacity-60">Hours</p>
        </div>
      </div>
      {features.length > 0 && (
        <div className="mt-4 text-center">
          <p className="text-xs opacity-60">{featureCount} new features including:</p>
          <div className="mt-1 flex flex-wrap justify-center gap-1">
            {features.map(f => (
              <span key={f} className="rounded-full bg-white/15 px-2 py-0.5 text-xs">{f}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
