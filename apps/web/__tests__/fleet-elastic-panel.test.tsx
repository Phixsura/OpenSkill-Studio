import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetElasticPanel } from "@/components/fleet-elastic-panel";
describe("FleetElasticPanel", () => { it("renders", () => {
    const { container } = render(<FleetElasticPanel status="green" nodes={5} activeShards={200} unassignedShards={0} />);
    expect(container.textContent).toContain("ElasticSearch");
    expect(container.textContent).toContain("GREEN");
}); });
