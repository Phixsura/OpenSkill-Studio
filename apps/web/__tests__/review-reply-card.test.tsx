import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewReplyCard } from "@/components/review-reply-card";

describe("ReviewReplyCard", () => {
  it("renders review without reply", () => {
    const review = { reviewId: "r1", userName: "Alice", rating: 4, comment: "Great extension!" };
    const { container } = render(<ReviewReplyCard review={review} />);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Great extension!");
    expect(container.querySelector("textarea")).toBeTruthy();
  });
  it("renders review with reply", () => {
    const review = { reviewId: "r1", userName: "Bob", rating: 5, comment: "Love it", reply: { content: "Thank you!" } };
    const { container } = render(<ReviewReplyCard review={review} />);
    expect(container.textContent).toContain("Developer Reply");
    expect(container.textContent).toContain("Thank you!");
  });
});
