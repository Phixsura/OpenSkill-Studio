import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDatadogPanel } from "@/components/fleet-datadog-panel";
describe("FleetDatadogPanel", () => { it("renders", () => {
    const { container } = render(<FleetDatadogPanel total={5} active={5} monitors={200} alertsFiring={5} />);
    expect(container.textContent).toContain("Datadog");
    expect(container.textContent).toContain("5 alerts");
}); });
