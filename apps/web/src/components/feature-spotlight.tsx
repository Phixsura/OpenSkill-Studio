"use client";

interface Feature { featureId: string; title: string; description: string; icon: string; category: string; }

export function FeatureSpotlight({ features, onDismiss }: {
  features: Feature[]; onDismiss?: (id: string) => void;
}) {
  if (!features.length) return null;
  return (
    <div className="space-y-2">
      {features.map((f) => (
        <div key={f.featureId} className="rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/10 dark:to-purple-900/10 border border-blue-200 dark:border-blue-800 p-4 flex items-start justify-between">
          <div className="flex gap-3">
            <span className="text-2xl">{f.icon}</span>
            <div>
              <span className="font-bold text-sm">New: {f.title}</span>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">{f.description}</p>
            </div>
          </div>
          <button onClick={() => onDismiss?.(f.featureId)} className="text-xs text-gray-400">✕</button>
        </div>
      ))}
    </div>
  );
}
