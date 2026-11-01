"use client";

interface EncryptedConfigViewerProps { config: Record<string, string>; encryptedFields: string[]; onDecrypt: (field: string) => void; }

export function EncryptedConfigViewer({ config, encryptedFields, onDecrypt }: EncryptedConfigViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Configuration</h3>
      <ul className="mt-3 space-y-1">
        {Object.entries(config).map(([key, value]) => {
          const isEncrypted = encryptedFields.includes(key);
          return (
            <li key={key} className="flex items-center justify-between rounded bg-gray-50 px-3 py-1.5 text-xs dark:bg-gray-800">
              <span className="font-mono font-medium">{key}</span>
              <div className="flex items-center gap-2">
                {isEncrypted ? (
                  <>
                    <span className="text-gray-400">🔒 encrypted</span>
                    <button onClick={() => onDecrypt(key)} className="text-blue-600 hover:underline">Reveal</button>
                  </>
                ) : (
                  <span className="text-gray-600 dark:text-gray-400">{value}</span>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
