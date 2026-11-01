import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSwitcherDropdown } from "@/components/app-switcher-dropdown";

describe("AppSwitcherDropdown", () => {
  const apps = [
    { id: "a1", name: "Auth SDK", icon: "A", status: "active", installs: 5000, current: true },
    { id: "a2", name: "Charts", icon: "C", status: "active", installs: 3000, current: false },
  ];
  it("renders", () => {
    const { container } = render(
      <AppSwitcherDropdown apps={apps} currentApp={apps[0]} onSwitch={vi.fn()} onCreateNew={vi.fn()} />
    );
    expect(container.textContent).toContain("Current App");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Charts");
    expect(container.textContent).toContain("Create New App");
  });
  it("switch", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppSwitcherDropdown apps={apps} currentApp={apps[0]} onSwitch={fn} onCreateNew={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Charts"))!);
    expect(fn).toHaveBeenCalledWith("a2");
  });
});
