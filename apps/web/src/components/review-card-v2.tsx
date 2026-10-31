"use client";

interface ReviewCardV2Props {
  title: string; rating: number; body: string;
  pros: string[]; cons: string[]; verifiedPurchase: boolean;
  helpfulYes: number; helpfulNo: number;
  onHelpful: (helpful: boolean) => void;
}

export function ReviewCardV2({ title, rating, body, pros, cons, verifiedPurchase, helpfulYes, helpfulNo, onHelpful }: ReviewCardV2Props) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-1">
            {Array.from({ length: 5 }, (_, i) => (
              <span key={i} className={i < rating ? "text-yellow-400" : "text-gray-300"}>★</span>
            ))}
          </div>
          <h4 className="mt-1 font-semibold">{title}</h4>
        </div>
        {verifiedPurchase && <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700">✓ Verified</span>}
      </div>
      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{body}</p>
      {(pros.length > 0 || cons.length > 0) && (
        <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
          {pros.length > 0 && <div><p className="font-medium text-green-600">👍 Pros</p>
            {pros.map((p, i) => <p key={i} className="text-gray-500">• {p}</p>)}</div>}
          {cons.length > 0 && <div><p className="font-medium text-red-600">👎 Cons</p>
            {cons.map((c, i) => <p key={i} className="text-gray-500">• {c}</p>)}</div>}
        </div>
      )}
      <div className="mt-3 flex items-center gap-3 text-xs text-gray-400">
        <span>Helpful?</span>
        <button onClick={() => onHelpful(true)} className="hover:text-green-600">👍 {helpfulYes}</button>
        <button onClick={() => onHelpful(false)} className="hover:text-red-600">👎 {helpfulNo}</button>
      </div>
    </div>
  );
}
