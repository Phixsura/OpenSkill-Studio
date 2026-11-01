import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCosmosdbPanel } from "@/components/fleet-cosmosdb-panel";
describe("FleetCosmosdbPanel", () => { it("renders", () => {
    const { container } = render(<FleetCosmosdbPanel accounts={3} available={3} consumedRu={150000} regions={5} />);
    expect(container.textContent).toContain("Cosmos DB");
    expect(container.textContent).toContain("5 regions");
}); });
