import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvSwitcher } from "@/components/env-switcher";

describe("EnvSwitcher", () => {
  it("renders envs", () => {
    const onSwitch = vi.fn();
    const { container, getByText } = render(
      <EnvSwitcher current="staging" onSwitch={onSwitch} environments={[
        { id: "development", label: "Dev", icon: "🔧", color: "blue", url: "" },
        { id: "staging", label: "Staging", icon: "🧪", color: "yellow", url: "" },
        { id: "production", label: "Production", icon: "🚀", color: "green", url: "" },
      ]} />
    );
    expect(container.textContent).toContain("Dev");
    expect(container.textContent).toContain("Staging");
    expect(container.textContent).toContain("Production");
    fireEvent.click(getByText("Production"));
    expect(onSwitch).toHaveBeenCalledWith("production");
  });
});
