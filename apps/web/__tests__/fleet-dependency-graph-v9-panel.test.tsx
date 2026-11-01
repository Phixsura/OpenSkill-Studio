import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDependencyGraphV9Panel } from "@/components/fleet-dependency-graph-v9-panel";
describe("FleetDependencyGraphV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDependencyGraphV9Panel nodes={300} edges={900} />);
    expect(container.textContent).toContain("Dependency Graph v9");
}); });
