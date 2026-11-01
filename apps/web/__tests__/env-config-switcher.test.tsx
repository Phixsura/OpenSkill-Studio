import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvConfigSwitcher } from "@/components/env-config-switcher";

describe("EnvConfigSwitcher", () => {
  it("renders environments", () => {
    const { container } = render(<EnvConfigSwitcher activeEnv="development" onSwitch={vi.fn()} />);
    expect(container.textContent).toContain("Development");
    expect(container.textContent).toContain("Staging");
    expect(container.textContent).toContain("Production");
  });
  it("calls onSwitch", () => {
    const fn = vi.fn();
    const { container } = render(<EnvConfigSwitcher activeEnv="development" onSwitch={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[2]); // production
    expect(fn).toHaveBeenCalledWith("production");
  });
});
