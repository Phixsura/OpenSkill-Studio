"use client";

interface WelcomeProps {
  greeting: string;
  displayName: string;
  extensionsCount: number;
  totalInstalls: number;
  recentActivity: string[];
  suggestedActions: string[];
  unreadNotifications: number;
  onboardingComplete: boolean;
}

export function WelcomeScreen({ greeting, displayName, extensionsCount, totalInstalls,
  recentActivity, suggestedActions, unreadNotifications, onboardingComplete }: WelcomeProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white">
        <h1 className="text-2xl font-bold">{greeting}</h1>
        {!onboardingComplete && (
          <p className="text-sm mt-2 opacity-80">Complete your setup to unlock all features</p>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <span className="text-3xl font-bold block">{extensionsCount}</span>
          <span className="text-sm text-gray-500">Extensions</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <span className="text-3xl font-bold block">{totalInstalls.toLocaleString()}</span>
          <span className="text-sm text-gray-500">Installs</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <span className="text-3xl font-bold block">{unreadNotifications}</span>
          <span className="text-sm text-gray-500">Notifications</span>
        </div>
      </div>

      {suggestedActions.length > 0 && (
        <div>
          <h3 className="text-sm font-bold mb-2">💡 Suggested Actions</h3>
          <div className="space-y-1">
            {suggestedActions.map((a, i) => (
              <div key={i} className="rounded-lg border dark:border-gray-700 p-2 text-sm flex items-center gap-2">
                <span className="text-blue-600">→</span> {a}
              </div>
            ))}
          </div>
        </div>
      )}

      {recentActivity.length > 0 && (
        <div>
          <h3 className="text-sm font-bold mb-2">📋 Recent Activity</h3>
          {recentActivity.map((a, i) => <p key={i} className="text-xs text-gray-500">• {a}</p>)}
        </div>
      )}
    </div>
  );
}
