import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceMapV9Panel } from "@/components/fleet-service-map-v9-panel";
describe("FleetServiceMapV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceMapV9Panel services={200} connections={600} />);
    expect(container.textContent).toContain("Service Map v9");
}); });
