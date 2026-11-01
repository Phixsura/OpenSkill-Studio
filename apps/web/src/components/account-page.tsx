"use client";

interface Profile { name: string; email: string; avatarUrl: string; bio: string; timezone: string; }
interface Security { twoFactorEnabled: boolean; activeSessions: number; passwordUpdated: string; }
interface Connection { provider: string; connected: boolean; username: string; }
interface AccountPageProps { profile: Profile; security: Security;
  connectedAccounts: Connection[]; sections: string[];
  onEditProfile: () => void; onEnable2FA: () => void; onConnect: (provider: string) => void; }

export function AccountPage({ profile, security, connectedAccounts, sections,
  onEditProfile, onEnable2FA, onConnect }: AccountPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="text-lg font-bold">👤 Account Settings</h2>
      <div className="flex items-center gap-4 rounded-xl border p-5 dark:border-gray-700">
        <img src={profile.avatarUrl} alt={profile.name} className="h-16 w-16 rounded-full" />
        <div className="flex-1">
          <h3 className="text-lg font-bold">{profile.name}</h3>
          <p className="text-sm text-gray-400">{profile.email}</p>
          {profile.bio && <p className="text-xs text-gray-500 mt-0.5">{profile.bio}</p>}
          <p className="text-xs text-gray-400 mt-0.5">🕐 {profile.timezone}</p>
        </div>
        <button onClick={onEditProfile} className="rounded border px-3 py-1.5 text-xs dark:border-gray-700">Edit</button>
      </div>
      <div className="rounded-xl border p-5 dark:border-gray-700">
        <h3 className="text-sm font-semibold mb-3">🔒 Security</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Two-Factor Authentication</span>
            {security.twoFactorEnabled ? (
              <span className="text-green-600 text-xs">✅ Enabled</span>
            ) : (
              <button onClick={onEnable2FA} className="text-xs text-blue-600">Enable</button>
            )}
          </div>
          <div className="flex justify-between">
            <span>Active Sessions</span>
            <span className="text-xs text-gray-400">{security.activeSessions}</span>
          </div>
          <div className="flex justify-between">
            <span>Password Updated</span>
            <span className="text-xs text-gray-400">{security.passwordUpdated}</span>
          </div>
        </div>
      </div>
      <div className="rounded-xl border p-5 dark:border-gray-700">
        <h3 className="text-sm font-semibold mb-3">🔗 Connected Accounts</h3>
        <div className="space-y-2">
          {connectedAccounts.map(c => (
            <div key={c.provider} className="flex items-center justify-between">
              <span className="text-sm">{c.provider}</span>
              {c.connected ? (
                <span className="text-xs text-green-600">✓ {c.username}</span>
              ) : (
                <button onClick={() => onConnect(c.provider)} className="text-xs text-blue-600">Connect</button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
