import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModerationQueuePanel } from "@/components/moderation-queue-panel";

describe("ModerationQueuePanel", () => {
  const items = [{
    queue_id: "mod_1", content_type: "review", content_id: "r1",
    reason: "Spam content", reported_by: "user_5", status: "pending", created_at: "2026-10-23",
  }];
  it("renders", () => {
    const { container } = render(
      <ModerationQueuePanel items={items} pendingCount={1} onApprove={vi.fn()} onReject={vi.fn()} />
    );
    expect(container.textContent).toContain("Moderation Queue");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("review");
    expect(container.textContent).toContain("Spam content");
  });
  it("reject", () => {
    const fn = vi.fn();
    const { container } = render(
      <ModerationQueuePanel items={items} pendingCount={1} onApprove={vi.fn()} onReject={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Reject")!);
    expect(fn).toHaveBeenCalledWith("mod_1");
  });
});
