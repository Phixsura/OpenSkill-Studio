"use client";

interface Props { pairCount: number; commitCount: number; backendTests: number; frontendTests: number; totalFiles: number; categories: string[]; achievedAt: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApi1000thPairMilestoneCard({ pairCount, commitCount, backendTests, frontendTests, totalFiles, categories, achievedAt, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-amber-400 bg-gradient-to-br from-amber-50 to-yellow-50 p-6 shadow-lg dark:border-amber-600 dark:from-gray-900 dark:to-amber-950/20">
      <div className="mb-4 text-center">
        <div className="text-4xl">🏆</div>
        <h3 className="mt-2 text-lg font-bold text-amber-700 dark:text-amber-400">1000 PAIRS MILESTONE!</h3>
        <p className="text-sm text-amber-600 dark:text-amber-500">LEGENDARY ACHIEVEMENT UNLOCKED</p>
        <p className="mt-1 text-xs text-gray-500">{appName} — {achievedAt}</p>
      </div>
      <div className="mb-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-white/80 p-2 dark:bg-gray-800/80">
          <div className="text-2xl font-bold text-amber-600">{pairCount.toLocaleString()}</div>
          <div className="text-[10px] text-gray-500">Pairs</div>
        </div>
        <div className="rounded-lg bg-white/80 p-2 dark:bg-gray-800/80">
          <div className="text-2xl font-bold text-amber-600">{commitCount.toLocaleString()}</div>
          <div className="text-[10px] text-gray-500">Commits</div>
        </div>
        <div className="rounded-lg bg-white/80 p-2 dark:bg-gray-800/80">
          <div className="text-2xl font-bold text-amber-600">{(backendTests + frontendTests).toLocaleString()}</div>
          <div className="text-[10px] text-gray-500">Tests</div>
        </div>
      </div>
      <div className="mb-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div className="rounded bg-white/60 p-1.5 dark:bg-gray-800/60"><span className="font-bold text-blue-600">{backendTests.toLocaleString()}</span> backend tests</div>
        <div className="rounded bg-white/60 p-1.5 dark:bg-gray-800/60"><span className="font-bold text-purple-600">{frontendTests.toLocaleString()}</span> frontend tests</div>
      </div>
      <div className="text-center text-[10px] text-gray-500">
        <div className="mb-1 font-medium">Categories covered:</div>
        <div className="flex flex-wrap justify-center gap-1">
          {categories.slice(0, 12).map((c) => (
            <span key={c} className="rounded bg-amber-100 px-1.5 py-0.5 text-[8px] text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">{c}</span>
          ))}
          {categories.length > 12 && <span className="text-amber-500">+{categories.length - 12} more</span>}
        </div>
      </div>
    </div>
  );
}
