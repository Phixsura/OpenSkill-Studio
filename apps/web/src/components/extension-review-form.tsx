"use client";

import { useState } from "react";

export function ExtensionReviewForm({
  extensionName,
  onSubmit,
}: {
  extensionName: string;
  onSubmit?: (review: { rating: number; title: string; body: string }) => void;
}) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (rating > 0 && title.trim()) {
      onSubmit?.({ rating, title: title.trim(), body: body.trim() });
      setSubmitted(true);
    }
  };

  if (submitted) {
    return (
      <div className="rounded-xl border dark:border-gray-700 p-6 text-center space-y-3">
        <div className="text-4xl">🎉</div>
        <h3 className="font-bold">Thank you for your review!</h3>
        <p className="text-sm text-gray-500">Your review of {extensionName} has been submitted.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 space-y-4 max-w-md">
      <h2 className="font-bold">⭐ Review {extensionName}</h2>

      {/* Star rating */}
      <div>
        <label className="block text-sm font-medium mb-2">Rating</label>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button key={star}
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoveredStar(star)}
              onMouseLeave={() => setHoveredStar(0)}
              className="text-2xl transition-transform hover:scale-110">
              {star <= (hoveredStar || rating) ? "★" : "☆"}
            </button>
          ))}
          {rating > 0 && <span className="text-sm text-gray-500 ml-2 self-center">{rating}/5</span>}
        </div>
      </div>

      {/* Title */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Title <span className="text-red-500">*</span>
        </label>
        <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
          placeholder="Summarize your experience..."
          className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
      </div>

      {/* Body */}
      <div>
        <label className="block text-sm font-medium mb-1">Review</label>
        <textarea value={body} onChange={(e) => setBody(e.target.value)}
          placeholder="Tell others about your experience..."
          rows={4}
          className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
      </div>

      <button onClick={handleSubmit}
        disabled={rating === 0 || !title.trim()}
        className="w-full rounded-lg bg-blue-600 text-white py-2.5 text-sm font-medium disabled:opacity-50">
        Submit Review
      </button>
    </div>
  );
}
