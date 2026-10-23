import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewReplyForm } from "@/components/review-reply-form";

describe("ReviewReplyForm", () => {
  it("renders review context", () => {
    const { container } = render(
      <ReviewReplyForm reviewId="r1" reviewerName="Alice" reviewText="Great app!" rating={5} onSubmit={vi.fn()} />
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Great app!");
    expect(container.textContent).toContain("Your Reply");
  });
  it("disabled initially", () => {
    const { container } = render(
      <ReviewReplyForm reviewId="r1" reviewerName="X" reviewText="Y" rating={3} onSubmit={vi.fn()} />
    );
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Reply") as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });
});
