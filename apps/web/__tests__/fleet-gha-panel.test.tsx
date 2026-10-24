import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGhaPanel } from "@/components/fleet-gha-panel";
describe("FleetGhaPanel", () => { it("renders", () => {
    const { container } = render(<FleetGhaPanel total={100} success={90} failure={10} billableMin={500} successRate={90} />);
    expect(container.textContent).toContain("GitHub Actions");
    expect(container.textContent).toContain("90% success");
}); });
