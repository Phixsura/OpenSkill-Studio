import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTestCovPanel } from "@/components/fleet-test-cov-panel";
describe("FleetTestCovPanel", () => { it("renders", () => {
    const { container } = render(<FleetTestCovPanel coveragePct={85} meetsTarget={true} totalLines={50000} />);
    expect(container.textContent).toContain("Test Coverage");
    expect(container.textContent).toContain("85%");
}); });
