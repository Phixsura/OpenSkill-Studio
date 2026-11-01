import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiObservabilityV9Panel } from "@/components/fleet-api-observability-v9-panel";
describe("FleetApiObservabilityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiObservabilityV9Panel apis={100} instrumented={100} />);
    expect(container.textContent).toContain("API Observability v9");
}); });
