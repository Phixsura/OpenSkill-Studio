import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDependencyScannerV9Panel } from "@/components/fleet-dependency-scanner-v9-panel";
describe("FleetDependencyScannerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDependencyScannerV9Panel deps={500} vulnerable={0} />);
    expect(container.textContent).toContain("Dependency Scanner v9");
}); });
