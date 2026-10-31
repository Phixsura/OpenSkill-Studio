import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNewrelicPanel } from "@/components/fleet-newrelic-panel";
describe("FleetNewrelicPanel", () => { it("renders", () => {
    const { container } = render(<FleetNewrelicPanel total={20} reporting={20} apdex={0.95} errorRate={0.5} />);
    expect(container.textContent).toContain("New Relic");
    expect(container.textContent).toContain("Apdex 0.95");
}); });
