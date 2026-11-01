import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSlaMgrPanel } from "@/components/fleet-ai-sla-mgr-panel";
describe("FleetAiSlaMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSlaMgrPanel slas={10} active={10} met={10} breached={0} uptime={99.99} />);
    expect(container.textContent).toContain("SLA Manager");
}); });
