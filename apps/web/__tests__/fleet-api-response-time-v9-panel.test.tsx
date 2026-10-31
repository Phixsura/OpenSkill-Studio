import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiResponseTimeV9Panel } from "@/components/fleet-api-response-time-v9-panel";
describe("FleetApiResponseTimeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiResponseTimeV9Panel endpoints={200} avgMs={25} />);
    expect(container.textContent).toContain("API Response Time v9");
}); });
