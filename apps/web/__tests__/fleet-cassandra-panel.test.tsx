import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCassandraPanel } from "@/components/fleet-cassandra-panel";
describe("FleetCassandraPanel", () => { it("renders", () => {
    const { container } = render(<FleetCassandraPanel nodes={9} up={8} down={1} totalLoad={4000} />);
    expect(container.textContent).toContain("Cassandra");
    expect(container.textContent).toContain("1 nodes down");
}); });
