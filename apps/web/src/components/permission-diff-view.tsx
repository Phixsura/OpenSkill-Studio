"use client";

interface PermissionDiffViewProps {
  added: string[];
  removed: string[];
  unchanged: string[];
  breaking: boolean;
  needsConsent: boolean;
}

export function PermissionDiffView({ added, removed, unchanged, breaking, needsConsent }: PermissionDiffViewProps) {
  const noChanges = added.length === 0 && removed.length === 0;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-2 flex items-center gap-2">
        <h4 className="font-semibold">Permission Changes</h4>
        {breaking && <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800">Breaking</span>}
        {needsConsent && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-800">Consent</span>}
      </div>
      {noChanges ? (
        <p className="text-sm text-gray-500">No permission changes</p>
      ) : (
        <div className="space-y-2">
          {added.length > 0 && (
            <div>
              <span className="text-xs font-medium text-green-600">+ Added</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {added.map(p => <span key={p} className="rounded bg-green-100 px-1.5 py-0.5 text-xs dark:bg-green-900">{p}</span>)}
              </div>
            </div>
          )}
          {removed.length > 0 && (
            <div>
              <span className="text-xs font-medium text-red-600">- Removed</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {removed.map(p => <span key={p} className="rounded bg-red-100 px-1.5 py-0.5 text-xs dark:bg-red-900">{p}</span>)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
