import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMicroserviceHealthV9Panel } from "@/components/fleet-microservice-health-v9-panel";
describe("FleetMicroserviceHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMicroserviceHealthV9Panel services={300} healthy={300} />);
    expect(container.textContent).toContain("Microservice Health v9");
}); });
