import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppUpdateBanner } from "@/components/app-update-banner";

describe("AppUpdateBanner", () => {
  it("renders updates", () => {
    const onUpdate = vi.fn();
    const { container, getByText } = render(
      <AppUpdateBanner summary="2 updates available" hasBreaking={true} onUpdateAll={onUpdate}
        updates={[
          { name: "Slack Bot", icon: "💬", current: "2.0", latest: "2.1", breaking: false },
          { name: "Analytics", icon: "📊", current: "3.0", latest: "4.0", breaking: true },
        ]} />
    );
    expect(container.textContent).toContain("2 updates available");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("2.0 → 2.1");
    expect(container.textContent).toContain("Analytics");
    fireEvent.click(getByText("Update All"));
    expect(onUpdate).toHaveBeenCalled();
  });
});
