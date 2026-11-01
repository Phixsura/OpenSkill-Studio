import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureGateManager } from "@/components/feature-gate-manager";

describe("FeatureGateManager", () => {
  const gates = [
    { type: "plan", feature: "SSO", config: { plans: ["enterprise"] } },
    { type: "role", feature: "Admin Panel", config: { roles: ["admin"] } },
  ];
  it("renders", () => {
    const { container } = render(<FeatureGateManager gates={gates} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("Feature Gates");
    expect(container.textContent).toContain("SSO");
    expect(container.textContent).toContain("💳");
    expect(container.textContent).toContain("Admin Panel");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(<FeatureGateManager gates={gates} onAdd={vi.fn()} onRemove={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Remove")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
