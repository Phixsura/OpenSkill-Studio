import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScopeSelectorGrid } from "@/components/scope-selector-grid";

describe("ScopeSelectorGrid", () => {
  const categories = {
    Apps: [{ id: "apps:read", description: "Read apps", risk: "low", granted: true }],
    Billing: [{ id: "billing:write", description: "Manage billing", risk: "high", granted: false }],
  };
  it("renders scopes", () => {
    const { container } = render(
      <ScopeSelectorGrid categories={categories} granted={1} totalScopes={8}
        hasHighRisk={false} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("apps:read");
    expect(container.textContent).toContain("billing:write");
    expect(container.textContent).toContain("1/8");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("Billing");
  });
});
