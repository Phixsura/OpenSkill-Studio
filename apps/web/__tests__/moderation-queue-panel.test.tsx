import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModerationQueuePanel } from "@/components/moderation-queue-panel";

const items = [
  { itemId: "m1", contentType: "review", content: "Great extension!", authorId: "u1", status: "pending", extensionId: "ext-1" },
  { itemId: "m2", contentType: "review", content: "Suspicious content", authorId: "u2", status: "escalated", extensionId: "ext-2" },
];

describe("ModerationQueuePanel", () => {
  it("renders queue", () => {
    const { container } = render(<ModerationQueuePanel items={items} />);
    expect(container.textContent).toContain("2 items pending");
    expect(container.textContent).toContain("Great extension!");
  });
  it("approve action", () => {
    const fn = vi.fn();
    const { container } = render(<ModerationQueuePanel items={items} onAction={fn} />);
    const approveBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Approve"));
    if (approveBtn) fireEvent.click(approveBtn);
    expect(fn).toHaveBeenCalledWith("m1", "approved");
  });
});
