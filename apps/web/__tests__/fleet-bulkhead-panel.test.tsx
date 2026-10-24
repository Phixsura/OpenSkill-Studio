import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBulkheadPanel } from "@/components/fleet-bulkhead-panel";
describe("FleetBulkheadPanel", () => { it("renders", () => {
    const { container } = render(<FleetBulkheadPanel pools={5} active={18} max={20} rejected={5} utilPct={90} healthy={false} />);
    expect(container.textContent).toContain("Bulkhead");
    expect(container.textContent).toContain("5 rejected");
}); });
