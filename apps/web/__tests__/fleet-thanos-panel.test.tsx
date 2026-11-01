import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetThanosPanel } from "@/components/fleet-thanos-panel";
describe("FleetThanosPanel", () => { it("renders", () => {
    const { container } = render(<FleetThanosPanel stores={5} healthy={5} compactionOk={4} allHealthy={true} />);
    expect(container.textContent).toContain("Thanos");
    expect(container.textContent).toContain("4 compaction OK");
}); });
