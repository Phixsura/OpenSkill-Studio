import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiIntegrationV9Panel } from "@/components/fleet-api-integration-v9-panel";
describe("FleetApiIntegrationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiIntegrationV9Panel integrations={30} calls={500000} />);
    expect(container.textContent).toContain("API Integration v9");
}); });
