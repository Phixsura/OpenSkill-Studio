import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccessReviewPanel } from "@/components/access-review-panel";

describe("AccessReviewPanel", () => {
  it("renders review", () => {
    const { container } = render(
      <AccessReviewPanel reviewed={1} total={2} onDecide={vi.fn()} items={[
        { userId: "u1", role: "admin", lastActiveDays: 5, decision: "approve" },
        { userId: "u2", role: "viewer", lastActiveDays: 90, decision: "pending" },
      ]} />
    );
    expect(container.textContent).toContain("Access Review");
    expect(container.textContent).toContain("1/2 reviewed");
    expect(container.textContent).toContain("u1");
    expect(container.textContent).toContain("approve");
    expect(container.textContent).toContain("u2");
    expect(container.textContent).toContain("90d inactive");
  });
});
