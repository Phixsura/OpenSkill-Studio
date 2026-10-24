import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAlertMgrPanel } from "@/components/fleet-ai-alert-mgr-panel";
describe("FleetAiAlertMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAlertMgrPanel managers={3} active={3} alerts={500} acked={490} silenced={10} channels={15} />);
    expect(container.textContent).toContain("Alert Manager");
}); });
