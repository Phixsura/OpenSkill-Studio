import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvironmentSwitcher } from "@/components/environment-switcher";

describe("EnvironmentSwitcher", () => {
  const envs = [
    { id: "development", label: "Dev", icon: "🔧", color: "blue", protected: false, active: true },
    { id: "staging", label: "Staging", icon: "🧪", color: "yellow", protected: false, active: false },
    { id: "production", label: "Prod", icon: "🚀", color: "green", protected: true, active: false },
  ];
  it("renders", () => {
    const { container } = render(
      <EnvironmentSwitcher environments={envs} current="development" onSwitch={vi.fn()} />
    );
    expect(container.textContent).toContain("Dev");
    expect(container.textContent).toContain("Staging");
    expect(container.textContent).toContain("Prod");
    expect(container.textContent).toContain("🔒");
  });
  it("switch", () => {
    const fn = vi.fn();
    const { container } = render(
      <EnvironmentSwitcher environments={envs} current="development" onSwitch={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("staging");
  });
});
