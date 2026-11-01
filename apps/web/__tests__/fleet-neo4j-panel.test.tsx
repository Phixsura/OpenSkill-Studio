import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNeo4jPanel } from "@/components/fleet-neo4j-panel";
describe("FleetNeo4jPanel", () => { it("renders", () => {
    const { container } = render(<FleetNeo4jPanel instances={3} available={3} nodes={3000000} relationships={15000000} />);
    expect(container.textContent).toContain("Neo4j");
    expect(container.textContent).toContain("3,000,000 nodes");
}); });
