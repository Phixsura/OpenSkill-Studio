import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperInboxView } from "@/components/developer-inbox-view";

describe("DeveloperInboxView", () => {
  const messages = [
    { message_id: "m1", type: "review", type_label: "New Review", icon: "⭐",
      title: "5-star review!", body: "Great app", read: false, created_at: "2026-10-23T12:00:00" },
    { message_id: "m2", type: "system", type_label: "System", icon: "🔔",
      title: "Update available", body: "v2.0", read: true, created_at: "2026-10-22T10:00:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <DeveloperInboxView messages={messages} unreadCount={1} onRead={vi.fn()} onReadAll={vi.fn()} />
    );
    expect(container.textContent).toContain("Inbox");
    expect(container.textContent).toContain("5-star review!");
    expect(container.textContent).toContain("⭐");
    expect(container.textContent).toContain("New Review");
    expect(container.textContent).toContain("Mark all read");
  });
  it("read", () => {
    const fn = vi.fn();
    const { container } = render(
      <DeveloperInboxView messages={messages} unreadCount={1} onRead={fn} onReadAll={vi.fn()} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]); // first message
    expect(fn).toHaveBeenCalledWith("m1");
  });
});
