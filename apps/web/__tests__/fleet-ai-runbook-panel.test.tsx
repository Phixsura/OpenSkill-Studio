import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRunbookPanel } from "@/components/fleet-ai-runbook-panel";
describe("FleetAiRunbookPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRunbookPanel runbooks={20} active={20} executions={500} autoResolved={450} duration={30} />);
    expect(container.textContent).toContain("Runbook");
}); });
