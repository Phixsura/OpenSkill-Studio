import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewModerationPanel } from "@/components/review-moderation-panel";

describe("ReviewModerationPanel", () => {
  it("renders reviews", () => {
    const onApprove = vi.fn();
    const { container, getByText } = render(
      <ReviewModerationPanel approvalRate={67} onApprove={onApprove} onReject={vi.fn()}
        reviews={[
          { safeBody: "Great app!", rating: 5, status: "approved", flags: [] },
          { safeBody: "Meh", rating: 3, status: "flagged", flags: ["too_short"] },
        ]} />
    );
    expect(container.textContent).toContain("Review Moderation");
    expect(container.textContent).toContain("67% approval rate");
    expect(container.textContent).toContain("Great app!");
    expect(container.textContent).toContain("approved");
    expect(container.textContent).toContain("flagged");
    expect(container.textContent).toContain("too_short");
    fireEvent.click(getByText("Approve"));
    expect(onApprove).toHaveBeenCalledWith(1);
  });
});
