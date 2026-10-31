import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewQueueTable } from "@/components/review-queue-table";

const ITEMS = [
  { appId: "a1", appName: "App One", version: "1.0.0", submittedBy: "u1", submittedAt: "2026-01-01", status: "pending" },
  { appId: "a2", appName: "App Two", version: "2.0.0", submittedBy: "u2", submittedAt: "2026-01-02", status: "in_review", reviewerId: "r1" },
];

describe("ReviewQueueTable", () => {
  it("shows items", () => {
    const { container } = render(<ReviewQueueTable items={ITEMS} />);
    expect(container.textContent).toContain("App One");
    expect(container.textContent).toContain("App Two");
  });

  it("shows status badges", () => {
    const { container } = render(<ReviewQueueTable items={ITEMS} />);
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("in_review");
  });

  it("empty state", () => {
    const { container } = render(<ReviewQueueTable items={[]} />);
    expect(container.textContent).toContain("No reviews");
  });

  it("shows assign button for pending", () => {
    const { container } = render(<ReviewQueueTable items={ITEMS} onAssign={vi.fn()} />);
    expect(container.textContent).toContain("Assign");
  });
});
