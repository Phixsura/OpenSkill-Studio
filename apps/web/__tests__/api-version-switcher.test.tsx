import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiVersionSwitcher } from "@/components/api-version-switcher";

describe("ApiVersionSwitcher", () => {
  it("renders versions", () => {
    const { container } = render(
      <ApiVersionSwitcher versions={["v1", "v2"]} active="v2" onSwitch={vi.fn()} />
    );
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("v2");
  });
  it("marks deprecated", () => {
    const { container } = render(
      <ApiVersionSwitcher versions={["v1", "v2"]} active="v2" onSwitch={vi.fn()} deprecated={["v1"]} />
    );
    expect(container.textContent).toContain("deprecated");
  });
  it("calls onSwitch", () => {
    const fn = vi.fn();
    const { container } = render(<ApiVersionSwitcher versions={["v1", "v2"]} active="v1" onSwitch={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("v2");
  });
});
