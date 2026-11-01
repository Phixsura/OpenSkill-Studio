import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRunbookPanel } from "@/components/fleet-runbook-panel";
describe("FleetRunbookPanel", () => { it("renders", () => {
    const { container } = render(<FleetRunbookPanel total={3} success={2} failed={1} successRate={66.7} />);
    expect(container.textContent).toContain("Runbook Automation");
    expect(container.textContent).toContain("66.7%");
}); });
