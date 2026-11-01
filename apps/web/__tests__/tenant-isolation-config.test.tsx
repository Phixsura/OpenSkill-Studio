import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TenantIsolationConfig } from "@/components/tenant-isolation-config";

describe("TenantIsolationConfig", () => {
  const levels = [
    { id: "shared", label: "Shared", risk: "low", cost_multiplier: 1.0, features: ["row_level_security"] },
    { id: "dedicated", label: "Dedicated", risk: "minimal", cost_multiplier: 2.5, features: ["separate_compute"] },
  ];
  it("renders", () => {
    const { container } = render(
      <TenantIsolationConfig levels={levels} currentLevel="shared" onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Tenant Isolation");
    expect(container.textContent).toContain("Shared");
    expect(container.textContent).toContain("Current");
    expect(container.textContent).toContain("2.5×");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(
      <TenantIsolationConfig levels={levels} currentLevel="shared" onSelect={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Select")!);
    expect(fn).toHaveBeenCalledWith("dedicated");
  });
});
