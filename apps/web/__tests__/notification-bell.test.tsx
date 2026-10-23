import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationBell } from "@/components/notification-bell";

describe("NotificationBell", () => {
  it("renders notifications", () => {
    const onMarkAll = vi.fn();
    const { container, getByText } = render(
      <NotificationBell unreadCount={2} onMarkRead={vi.fn()} onMarkAllRead={onMarkAll}
        notifications={[
          { id: "n1", title: "Welcome!", body: "", category: "onboarding", read: false },
          { id: "n2", title: "Deploy done", body: "v2.0", category: "deploy", read: false },
        ]} />
    );
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("2");
    expect(container.textContent).toContain("Welcome!");
    expect(container.textContent).toContain("Deploy done");
    fireEvent.click(getByText("Mark all read"));
    expect(onMarkAll).toHaveBeenCalled();
  });
});
