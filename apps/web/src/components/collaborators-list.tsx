"use client";

interface Collaborator { id: string; name: string; email: string; role: string;
  roleIcon: string; canDeploy: boolean; canPublish: boolean; }
interface CollaboratorsListProps { collaborators: Collaborator[]; appName: string;
  onRemove: (id: string) => void; onInvite: () => void; }

export function CollaboratorsList({ collaborators, appName, onRemove, onInvite }: CollaboratorsListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">👥 {appName} Collaborators</h3>
        <button onClick={onInvite} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">+ Invite</button>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {collaborators.map(c => (
          <div key={c.id} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-200 text-sm dark:bg-gray-700">
                {c.name[0]?.toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-medium">{c.name}</p>
                <p className="text-xs text-gray-400">{c.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs">{c.roleIcon} {c.role}</span>
              {c.role !== "owner" && (
                <button onClick={() => onRemove(c.id)} className="text-xs text-red-600 hover:underline">Remove</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
