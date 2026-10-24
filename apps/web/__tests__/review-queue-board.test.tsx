import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewQueueBoard } from "@/components/review-queue-board";

describe("ReviewQueueBoard", () => {
  it("renders queue", () => {
    const { container } = render(
      <ReviewQueueBoard pendingCount={2} onAdvance={vi.fn()}
        stages={{
          submitted: [{ appName: "App A", developer: "Dev 1", submittedAt: "", stage: "submitted" }],
          automated_scan: [],
          manual_review: [{ appName: "App B", developer: "Dev 2", submittedAt: "", stage: "manual_review" }],
          approved: [],
          rejected: [],
        }} />
    );
    expect(container.textContent).toContain("Review Queue");
    expect(container.textContent).toContain("2 pending");
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("App B");
    expect(container.textContent).toContain("Submitted");
    expect(container.textContent).toContain("Manual Review");
  });
});
