import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMaturityPanel } from "@/components/fleet-maturity-panel";
describe("FleetMaturityPanel", () => { it("renders", () => {
    const { container } = render(<FleetMaturityPanel score={84} level="Advanced" />);
    expect(container.textContent).toContain("Platform Maturity");
    expect(container.textContent).toContain("84 — Advanced");
}); });
