import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppNotificationBell } from "@/components/app-notification-bell";

describe("AppNotificationBell", () => {
  it("shows bell", () => {
    const { container } = render(<AppNotificationBell count={0} />);
    expect(container.textContent).toContain("🔔");
  });

  it("shows count badge", () => {
    const { container } = render(<AppNotificationBell count={5} />);
    expect(container.textContent).toContain("5");
  });

  it("caps at 99+", () => {
    const { container } = render(<AppNotificationBell count={150} />);
    expect(container.textContent).toContain("99+");
  });

  it("hides badge at 0", () => {
    const { container } = render(<AppNotificationBell count={0} />);
    expect(container.querySelector("[class*='bg-red']")).toBeNull();
  });

  it("calls onClick", () => {
    const onClick = vi.fn();
    const { container } = render(<AppNotificationBell count={3} onClick={onClick} />);
    fireEvent.click(container.querySelector("button")!);
    expect(onClick).toHaveBeenCalled();
  });
});
