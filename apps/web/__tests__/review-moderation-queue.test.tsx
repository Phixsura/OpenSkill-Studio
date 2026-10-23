import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewModerationQueue } from "@/components/review-moderation-queue";

describe("ReviewModerationQueue", () => {
  const reviews = [{
    id: "r1", text: "Bad app", rating: 1,
    flags: [{ type: "low_effort", detail: "short" }], action: "review",
  }];
  it("renders", () => {
    const { container } = render(
      <ReviewModerationQueue reviews={reviews} onApprove={vi.fn()} onReject={vi.fn()} />
    );
    expect(container.textContent).toContain("Moderation Queue");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("Bad app");
  });
  it("approve/reject", () => {
    const approve = vi.fn(), reject = vi.fn();
    const { container } = render(
      <ReviewModerationQueue reviews={reviews} onApprove={approve} onReject={reject} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Approve")!);
    expect(approve).toHaveBeenCalledWith("r1");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Reject")!);
    expect(reject).toHaveBeenCalledWith("r1");
  });
});
