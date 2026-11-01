import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFinalStatusPanel } from "@/components/fleet-final-status-panel";
describe("FleetFinalStatusPanel", () => { it("renders", () => {
    const { container } = render(<FleetFinalStatusPanel />);
    expect(container.textContent).toContain("ALL SYSTEMS OPERATIONAL");
}); });
