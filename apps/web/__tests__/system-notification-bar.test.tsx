import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SystemNotificationBar } from "@/components/system-notification-bar";

describe("SystemNotificationBar", () => {
  const notifications = [
    { notification_id: "s1", title: "Maintenance", message: "DB upgrade", severity: "maintenance", dismissible: true },
  ];
  it("renders", () => {
    const { container } = render(<SystemNotificationBar notifications={notifications} onDismiss={vi.fn()} />);
    expect(container.textContent).toContain("Maintenance");
    expect(container.textContent).toContain("DB upgrade");
    expect(container.textContent).toContain("🔧");
  });
  it("dismiss", () => {
    const fn = vi.fn();
    const { container } = render(<SystemNotificationBar notifications={notifications} onDismiss={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "✕")!);
    expect(fn).toHaveBeenCalledWith("s1");
  });
  it("empty", () => {
    const { container } = render(<SystemNotificationBar notifications={[]} onDismiss={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });
});
