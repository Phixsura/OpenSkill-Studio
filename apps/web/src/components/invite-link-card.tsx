"use client";

interface InviteLinkInfo {
  invite_id: string;
  code: string;
  role: string;
  max_uses: number;
  uses: number;
  is_valid: boolean;
  created_by: string;
}

interface InviteLinkCardProps {
  links: InviteLinkInfo[];
  appName: string;
}

export default function InviteLinkCard({ links, appName }: InviteLinkCardProps) {
  const valid = links.filter((l) => l.is_valid).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔗 Invite Links
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {valid}/{links.length} valid
        </span>
      </div>

      {links.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invite links</p>
      ) : (
        <div className="space-y-1.5">
          {links.map((l) => (
            <div
              key={l.invite_id}
              className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!l.is_valid ? "opacity-50" : ""}`}
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-[11px] text-gray-600 dark:text-gray-400">
                  {l.code.slice(0, 8)}...
                </span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                  {l.role}
                </span>
              </div>
              <span className="text-[10px] text-gray-400">
                {l.uses}
                {l.max_uses > 0 ? `/${l.max_uses}` : ""} used
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
