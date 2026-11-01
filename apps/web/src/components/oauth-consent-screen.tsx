"use client";

interface OAuthConsentScreenProps {
  appName: string;
  appIcon?: string;
  developerName: string;
  scopes: string[];
  redirectUri: string;
  onApprove: () => void;
  onDeny: () => void;
}

const SCOPE_DESCRIPTIONS: Record<string, string> = {
  "read:cohorts": "View your cohorts",
  "write:cohorts": "Create and modify cohorts",
  "read:projects": "View your projects",
  "write:projects": "Create and modify projects",
  "read:submissions": "View submissions",
  "read:skills": "View skill data",
  "read:analytics": "View analytics data",
  "subscribe:events": "Receive event notifications",
  "extend:ui": "Add UI extensions",
  "run:background_jobs": "Run background processing",
};

export function OAuthConsentScreen({ appName, appIcon, developerName, scopes, redirectUri, onApprove, onDeny }: OAuthConsentScreenProps) {
  return (
    <div className="mx-auto max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 text-center">
        {appIcon && <span className="text-4xl">{appIcon}</span>}
        <h2 className="mt-2 text-xl font-bold">{appName}</h2>
        <p className="text-sm text-gray-500">by {developerName}</p>
      </div>

      <p className="mb-3 text-sm text-gray-600 dark:text-gray-400">
        This app is requesting access to:
      </p>

      <ul className="mb-4 space-y-2">
        {scopes.map(scope => (
          <li key={scope} className="flex items-center gap-2 rounded border border-gray-100 p-2 text-sm dark:border-gray-800">
            <span className="text-green-500">✓</span>
            <span>{SCOPE_DESCRIPTIONS[scope] ?? scope}</span>
          </li>
        ))}
      </ul>

      <p className="mb-4 text-xs text-gray-400">
        Will redirect to: {redirectUri}
      </p>

      <div className="flex gap-3">
        <button onClick={onDeny} className="flex-1 rounded border border-gray-300 px-4 py-2 text-sm hover:bg-gray-50 dark:border-gray-600">
          Deny
        </button>
        <button onClick={onApprove} className="flex-1 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
          Authorize
        </button>
      </div>
    </div>
  );
}
