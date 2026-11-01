"use client";

interface SigningKeyCardProps {
  name: string;
  fingerprint: string;
  createdAt: string;
  onDelete?: () => void;
}

export function SigningKeyCard({ name, fingerprint, createdAt, onDelete }: SigningKeyCardProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-gray-200 p-3 dark:border-gray-700">
      <div>
        <h4 className="text-sm font-semibold">{name}</h4>
        <code className="text-xs text-gray-500 dark:text-gray-400">{fingerprint}</code>
        <p className="text-xs text-gray-400">Added {createdAt}</p>
      </div>
      {onDelete && (
        <button onClick={onDelete} className="text-xs text-red-500 hover:text-red-700">Remove</button>
      )}
    </div>
  );
}
