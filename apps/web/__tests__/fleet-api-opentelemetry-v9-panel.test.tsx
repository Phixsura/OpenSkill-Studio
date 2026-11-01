import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiOpentelemetryV9Panel } from "@/components/fleet-api-opentelemetry-v9-panel";
describe("FleetApiOpentelemetryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiOpentelemetryV9Panel services={200} instrumented={200} />);
    expect(container.textContent).toContain("API OTel v9");
}); });
