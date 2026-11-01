import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetObservabilityHubV9Panel } from "@/components/fleet-observability-hub-v9-panel";
describe("FleetObservabilityHubV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetObservabilityHubV9Panel sources={20} mps={100000} />);
    expect(container.textContent).toContain("Observability Hub v9");
}); });
