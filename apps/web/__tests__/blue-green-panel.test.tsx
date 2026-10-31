import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BlueGreenPanel } from "@/components/blue-green-panel";

describe("BlueGreenPanel", () => {
  it("renders and switches", () => {
    const onSwitch = vi.fn();
    const { container, getByText } = render(
      <BlueGreenPanel active="green" onSwitch={onSwitch} onRollback={vi.fn()}
        slots={{
          blue: { version: "1.0", status: "idle", health: "healthy" },
          green: { version: "2.0", status: "active", health: "healthy" },
        }} />
    );
    expect(container.textContent).toContain("Blue-Green Deploy");
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("Active");
    fireEvent.click(getByText("Switch"));
    expect(onSwitch).toHaveBeenCalled();
  });
});
