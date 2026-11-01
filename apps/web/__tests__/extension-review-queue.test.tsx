import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionReviewQueue } from "@/components/extension-review-queue";

const mockItems = [
  { extensionId: "e1", name: "Slack Bot", author: "alice", version: "1.0.0",
    submittedAt: "2h ago", state: "submitted" as const, securityScore: 95, codeSize: "12KB" },
  { extensionId: "e2", name: "Analytics Widget", author: "bob", version: "2.1.0",
    submittedAt: "1d ago", state: "in_review" as const, securityScore: 78, codeSize: "45KB" },
];

describe("ExtensionReviewQueue", () => {
  it("renders queue items with states", () => {
    const { container } = render(<ExtensionReviewQueue items={mockItems} />);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Analytics Widget");
    expect(container.textContent).toContain("1 awaiting review");
    expect(container.textContent).toContain("1 in review");
  });

  it("shows Start Review for submitted items", () => {
    const onStart = vi.fn();
    const { getByText } = render(<ExtensionReviewQueue items={mockItems} onStartReview={onStart} />);
    fireEvent.click(getByText("Start Review"));
    expect(onStart).toHaveBeenCalledWith("e1");
  });

  it("shows Approve/Reject for in_review items", () => {
    const onApprove = vi.fn();
    const { getByText } = render(<ExtensionReviewQueue items={mockItems} onApprove={onApprove} />);
    expect(getByText("✅ Approve")).toBeDefined();
    expect(getByText("❌ Reject")).toBeDefined();
  });

  it("shows security scores", () => {
    const { container } = render(<ExtensionReviewQueue items={mockItems} />);
    expect(container.textContent).toContain("95/100");
    expect(container.textContent).toContain("78/100");
  });
});
