"use client";

interface AvatarUploaderProps { currentUrl: string; userName: string; initials: string;
  onUpload: (file: File) => void; uploading: boolean; }

export function AvatarUploader({ currentUrl, userName, initials, onUpload, uploading }: AvatarUploaderProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="relative">
        {currentUrl ? (
          <img src={currentUrl} alt={userName} className="w-16 h-16 rounded-full object-cover" />
        ) : (
          <div className="w-16 h-16 rounded-full bg-blue-500 flex items-center justify-center text-white text-xl font-bold">{initials}</div>
        )}
        <label className="absolute -bottom-1 -right-1 w-6 h-6 bg-white dark:bg-gray-900 border rounded-full flex items-center justify-center cursor-pointer shadow text-xs">
          📷
          <input type="file" accept=".png,.jpg,.jpeg,.webp" className="hidden" disabled={uploading}
            onChange={e => e.target.files?.[0] && onUpload(e.target.files[0])} />
        </label>
      </div>
      <div>
        <p className="text-sm font-medium">{userName}</p>
        <p className="text-xs text-gray-400">{uploading ? "Uploading..." : "Click camera to change"}</p>
      </div>
    </div>
  );
}
