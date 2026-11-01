import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSessionMgrPanel } from "@/components/fleet-ai-session-mgr-panel";
describe("FleetAiSessionMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSessionMgrPanel managers={3} active={3} sessions={500000} duration={30} persistence={99.5} />);
    expect(container.textContent).toContain("Session Manager");
}); });
