"use client";

interface Discussion { discussion_id: string; title: string; category: string; author_id: string;
  replies: number; upvotes: number; solved: boolean; created_at: string; }
interface CommunityDiscussionListProps { discussions: Discussion[]; onSelect: (id: string) => void; }

const catColors: Record<string, string> = {
  help: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", general: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  showcase: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", feedback: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  announcements: "bg-green-100 text-green-700 dark:bg-green-900/30",
};

export function CommunityDiscussionList({ discussions, onSelect }: CommunityDiscussionListProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Community Discussions</h2>
      {discussions.map(d => (
        <button key={d.discussion_id} onClick={() => onSelect(d.discussion_id)}
          className="flex w-full items-start gap-3 rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
          {d.solved && <span className="mt-0.5 text-green-500">✓</span>}
          <div className="flex-1">
            <p className="font-medium">{d.title}</p>
            <div className="mt-1 flex items-center gap-2 text-xs text-gray-400">
              <span className={`rounded-full px-1.5 py-0.5 ${catColors[d.category] ?? catColors.general}`}>{d.category}</span>
              <span>💬 {d.replies}</span>
              <span>👍 {d.upvotes}</span>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
