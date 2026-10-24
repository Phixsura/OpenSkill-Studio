import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosReportV9Panel } from "@/components/fleet-chaos-report-v9-panel";
describe("FleetChaosReportV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetChaosReportV9Panel reports={50} improvements={30} />);
    expect(container.textContent).toContain("Chaos Report v9");
}); });
