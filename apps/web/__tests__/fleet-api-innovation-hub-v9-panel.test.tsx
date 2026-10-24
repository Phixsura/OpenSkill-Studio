import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiInnovationHubV9Panel } from "@/components/fleet-api-innovation-hub-v9-panel";
describe("FleetApiInnovationHubV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiInnovationHubV9Panel experiments={20} graduated={10} />);
    expect(container.textContent).toContain("Innovation Hub v9");
}); });
