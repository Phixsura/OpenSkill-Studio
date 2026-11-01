import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewModerationPanel } from "@/components/review-moderation-panel";

const mockReviews = [
  { id: "m1", reviewId: "r1", author: "alice", content: "Great extension!",
    rating: 5, status: "approved" as const, autoFlags: [] },
  { id: "m2", reviewId: "r2", author: "spammer", content: "Buy now click here",
    rating: 5, status: "flagged" as const, autoFlags: ["spam_pattern"] },
  { id: "m3", reviewId: "r3", author: "bob", content: "Doesn't work at all",
    rating: 1, status: "appealed" as const, autoFlags: [],
    appealText: "I had a legitimate issue" },
];

describe("ReviewModerationPanel", () => {
  it("renders reviews with status", () => {
    const { container } = render(<ReviewModerationPanel reviews={mockReviews} />);
    expect(container.textContent).toContain("Review Moderation");
    expect(container.textContent).toContain("Great extension!");
    expect(container.textContent).toContain("Approved");
  });

  it("shows auto flags", () => {
    const { container } = render(<ReviewModerationPanel reviews={mockReviews} />);
    expect(container.textContent).toContain("spam_pattern");
  });

  it("shows appeal text", () => {
    const { container } = render(<ReviewModerationPanel reviews={mockReviews} />);
    expect(container.textContent).toContain("legitimate issue");
  });

  it("calls onApprove for flagged", () => {
    const onApprove = vi.fn();
    const { getAllByText } = render(
      <ReviewModerationPanel reviews={mockReviews} onApprove={onApprove} />
    );
    fireEvent.click(getAllByText("Approve")[0]);
    expect(onApprove).toHaveBeenCalledWith("m2");
  });
});
