import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackBoard } from "@/components/feedback-board";

describe("FeedbackBoard", () => {
  const columns = {
    open: [{ feedback_id: "f1", title: "Dark mode", category: "feature", status: "open", votes: 10 }],
    shipped: [{ feedback_id: "f2", title: "Bug fix", category: "bug", status: "shipped", votes: 5 }],
  };
  it("renders", () => {
    const { container } = render(
      <FeedbackBoard columns={columns} total={2} onVote={vi.fn()} onStatusChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Feedback Board");
    expect(container.textContent).toContain("2 items");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("Open");
    expect(container.textContent).toContain("Shipped");
  });
});
