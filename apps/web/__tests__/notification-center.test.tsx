import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationCenter } from "@/components/notification-center";

describe("NotificationCenter", () => {
  const notifs = [
    { id: "1", title: "New review", body: "Alice reviewed", icon: "⭐", type: "review", read: false, timestamp: "2026-01-02T00:00:00Z" },
    { id: "2", title: "Published", body: "App v2", icon: "🚀", type: "publish", read: true, timestamp: "2026-01-01T00:00:00Z" },
  ];
  it("renders notifications and badge", () => {
    const { container } = render(<NotificationCenter notifications={notifs} onMarkRead={vi.fn()} />);
    expect(container.textContent).toContain("New review");
    expect(container.textContent).toContain("Published");
    expect(container.textContent).toContain("1"); // unread badge
  });
  it("mark all read", () => {
    const fn = vi.fn();
    const { container } = render(<NotificationCenter notifications={notifs} onMarkRead={fn} />);
    const btn = container.querySelector("button")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith(["1"]);
  });
});
