import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationBadge } from "@/components/notification-badge";

describe("NotificationBadge", () => {
  it("renders with count", () => {
    const { container } = render(
      <NotificationBadge unread={5} display="5" hasUrgent={false} onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("🔔");
    expect(container.textContent).toContain("5");
  });
  it("hides when zero", () => {
    const { container } = render(
      <NotificationBadge unread={0} display="0" hasUrgent={false} onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("🔔");
    expect(container.textContent).not.toContain("0");
  });
  it("clicks", () => {
    const fn = vi.fn();
    const { container } = render(
      <NotificationBadge unread={3} display="3" hasUrgent={true} onClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
