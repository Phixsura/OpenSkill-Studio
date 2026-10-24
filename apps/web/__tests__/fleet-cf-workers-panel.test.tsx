import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCfWorkersPanel } from "@/components/fleet-cf-workers-panel";
describe("FleetCfWorkersPanel", () => { it("renders", () => {
    const { container } = render(<FleetCfWorkersPanel workers={20} active={20} requests={50000000} errors={0} avgCpu={3} />);
    expect(container.textContent).toContain("CF Workers");
    expect(container.textContent).toContain("50,000,000");
}); });
