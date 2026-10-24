import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BlueGreenSwitcher } from "@/components/blue-green-switcher";

describe("BlueGreenSwitcher", () => {
  it("renders switcher", () => {
    const { container } = render(
      <BlueGreenSwitcher service="api" activeSlot="blue"
        blueVersion="2.0" greenVersion="2.1"
        blueTraffic={100} greenTraffic={0} onSwitch={vi.fn()} />
    );
    expect(container.textContent).toContain("Blue-Green: api");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("v2.1");
    expect(container.textContent).toContain("100% traffic");
    expect(container.textContent).toContain("0% traffic");
    expect(container.textContent).toContain("Switch");
  });
});
