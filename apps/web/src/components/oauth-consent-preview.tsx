"use client";

interface OAuthConsentPreviewProps { appName: string; appIcon?: string; scopes: string[]; redirectUri: string; onApprove: () => void; onDeny: () => void; }

export function OAuthConsentPreview({ appName, appIcon, scopes, redirectUri, onApprove, onDeny }: OAuthConsentPreviewProps) {
  const domain = (() => { try { return new URL(redirectUri).hostname; } catch { return redirectUri; } })();
  return (
    <div className="mx-auto max-w-sm rounded-lg border border-gray-200 p-6 shadow-lg dark:border-gray-700">
      <div className="text-center">
        <span className="text-4xl">{appIcon || "🔐"}</span>
        <h2 className="mt-2 text-lg font-semibold">{appName} wants to access your account</h2>
        <p className="mt-1 text-xs text-gray-400">Redirecting to {domain}</p>
      </div>
      <div className="mt-4">
        <p className="text-sm font-medium">This app will be able to:</p>
        <ul className="mt-2 space-y-1">
          {scopes.map(s => (
            <li key={s} className="flex items-center gap-2 text-sm">
              <span className="text-green-500">✓</span> {s}
            </li>
          ))}
        </ul>
      </div>
      <div className="mt-6 flex gap-3">
        <button onClick={onDeny} className="flex-1 rounded border px-4 py-2 text-sm text-gray-600">Deny</button>
        <button onClick={onApprove} className="flex-1 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">Authorize</button>
      </div>
    </div>
  );
}
