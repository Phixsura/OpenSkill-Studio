import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCtCovPanel } from "@/components/fleet-ct-cov-panel";
describe("FleetCtCovPanel", () => { it("renders", () => {
    const { container } = render(<FleetCtCovPanel total={20} withTests={16} without={4} coveragePct={80} good={true} />);
    expect(container.textContent).toContain("Contract Tests");
    expect(container.textContent).toContain("80%");
}); });
