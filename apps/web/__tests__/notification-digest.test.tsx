import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotificationDigest } from "@/components/notification-digest";

describe("NotificationDigest", () => {
  it("shows highlights", () => {
    const { container } = render(<NotificationDigest period="daily" totalEvents={10} highlights={["📥 5 installs"]} byType={{ app_installed: 5 }} />);
    expect(container.textContent).toContain("5 installs");
  });
  it("shows empty state", () => {
    const { container } = render(<NotificationDigest period="weekly" totalEvents={0} highlights={[]} byType={{}} />);
    expect(container.textContent).toContain("No activity");
  });
  it("shows event count", () => {
    const { container } = render(<NotificationDigest period="daily" totalEvents={42} highlights={[]} byType={{}} />);
    expect(container.textContent).toContain("42 events");
  });
});
