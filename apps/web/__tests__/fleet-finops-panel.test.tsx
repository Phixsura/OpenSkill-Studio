import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFinopsPanel } from "@/components/fleet-finops-panel";
describe("FleetFinopsPanel", () => { it("renders", () => {
    const { container } = render(<FleetFinopsPanel score={80} level="Run" />);
    expect(container.textContent).toContain("FinOps");
    expect(container.textContent).toContain("80 — Run");
}); });
