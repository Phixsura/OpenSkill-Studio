import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetElasticachePanel } from "@/components/fleet-elasticache-panel";
describe("FleetElasticachePanel", () => { it("renders", () => {
    const { container } = render(<FleetElasticachePanel clusters={5} available={5} nodes={15} memoryPct={60} />);
    expect(container.textContent).toContain("ElastiCache");
    expect(container.textContent).toContain("60%");
}); });
