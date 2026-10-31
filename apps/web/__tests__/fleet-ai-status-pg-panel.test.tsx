import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStatusPgPanel } from "@/components/fleet-ai-status-pg-panel";
describe("FleetAiStatusPgPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStatusPgPanel components={10} operational={10} degraded={0} outage={0} overall="operational" />);
    expect(container.textContent).toContain("OPERATIONAL");
}); });
