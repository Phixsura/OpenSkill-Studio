"use client";

interface MarketplaceReadinessCardProps { ready: boolean; errors: string[]; warnings: string[]; }

export function MarketplaceReadinessCard({ ready, errors, warnings }: MarketplaceReadinessCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${ready ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20"}`}>
      <h4 className="mb-2 font-semibold">{ready ? "✅ Ready for Marketplace" : "⚠️ Not Ready Yet"}</h4>
      {errors.length > 0 && (
        <ul className="mb-2 space-y-1">{errors.map((e, i) => <li key={i} className="text-sm text-red-700">❌ {e}</li>)}</ul>
      )}
      {warnings.length > 0 && (
        <ul className="space-y-1">{warnings.map((w, i) => <li key={i} className="text-sm text-yellow-700">💡 {w}</li>)}</ul>
      )}
      {errors.length === 0 && warnings.length === 0 && <p className="text-sm text-green-700">All checks passed!</p>}
    </div>
  );
}
