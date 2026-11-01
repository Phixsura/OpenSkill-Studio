import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTemporalPanel } from "@/components/fleet-temporal-panel";
describe("FleetTemporalPanel", () => { it("renders", () => {
    const { container } = render(<FleetTemporalPanel namespaces={5} healthy={5} runningWorkflows={1000} completed={50000} />);
    expect(container.textContent).toContain("Temporal");
    expect(container.textContent).toContain("50,000");
}); });
