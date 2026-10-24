import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationCenter } from "@/components/notification-center";

describe("NotificationCenter", () => {
  it("renders notifications", () => {
    const { container } = render(
      <NotificationCenter unread={2} onMarkRead={vi.fn()} onMarkAllRead={vi.fn()}
        notifications={[
          { id: 2, title: "Alert", body: "CPU high", category: "alert", priority: "high", read: false },
          { id: 1, title: "Deploy Done", body: "v2.0 deployed", category: "deploy", priority: "normal", read: true },
        ]} />
    );
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("2");
    expect(container.textContent).toContain("Alert");
    expect(container.textContent).toContain("urgent");
    expect(container.textContent).toContain("Deploy Done");
    expect(container.textContent).toContain("Mark all read");
  });
});
