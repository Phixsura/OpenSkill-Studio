import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotificationDot } from "@/components/notification-dot";

describe("NotificationDot", () => {
  it("renders with count", () => {
    const { container } = render(
      <NotificationDot count={5} display="5" visible={true} color="red">
        <span>🔔</span>
      </NotificationDot>
    );
    expect(container.textContent).toContain("🔔");
    expect(container.textContent).toContain("5");
  });
  it("hidden when zero", () => {
    const { container } = render(
      <NotificationDot count={0} display="0" visible={false} color="red">
        <span>🔔</span>
      </NotificationDot>
    );
    expect(container.textContent).toContain("🔔");
    expect(container.textContent).not.toContain("0");
  });
});
