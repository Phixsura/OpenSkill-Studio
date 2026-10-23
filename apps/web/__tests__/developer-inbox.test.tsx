import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperInbox } from "@/components/developer-inbox";

describe("DeveloperInbox", () => {
  it("renders messages", () => {
    const msgs = [
      { from_type: "system", subject: "Welcome!", body: "Hi", priority: "normal", read: false, created_at: "2026-10-01" },
      { from_type: "review", subject: "New Review", body: "5 stars", priority: "urgent", read: true, created_at: "2026-10-02" },
    ];
    const { container } = render(<DeveloperInbox messages={msgs} onRead={vi.fn()} />);
    expect(container.textContent).toContain("Welcome!");
    expect(container.textContent).toContain("1 unread");
  });
  it("empty state", () => {
    const { container } = render(<DeveloperInbox messages={[]} onRead={vi.fn()} />);
    expect(container.textContent).toContain("Inbox empty");
  });
  it("calls onRead", () => {
    const fn = vi.fn();
    const msgs = [{ from_type: "system", subject: "X", body: "Y", priority: "normal", read: false, created_at: "" }];
    const { container } = render(<DeveloperInbox messages={msgs} onRead={fn} />);
    fireEvent.click(container.querySelector("li")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
