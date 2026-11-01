import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHcSummaryPanel } from "@/components/fleet-hc-summary-panel";
describe("FleetHcSummaryPanel", () => { it("renders", () => {
    const { container } = render(<FleetHcSummaryPanel total={10} passing={8} warning={1} failing={1} score={80} />);
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("80%");
}); });
