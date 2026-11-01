import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TenantSelector } from "@/components/tenant-selector";

describe("TenantSelector", () => {
  const tenants = [
    { id: "acme", name: "Acme Corp", plan: "Enterprise" },
    { id: "startup", name: "StartupXYZ", plan: "Pro" },
  ];
  it("renders", () => {
    const { container } = render(<TenantSelector tenants={tenants} currentTenant="acme" onSwitch={vi.fn()} />);
    expect(container.textContent).toContain("Organization");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("Enterprise");
    expect(container.textContent).toContain("✓");
  });
  it("switch", () => {
    const fn = vi.fn();
    const { container } = render(<TenantSelector tenants={tenants} currentTenant="acme" onSwitch={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("startup");
  });
});
