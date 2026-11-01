import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCronMgrPanel } from "@/components/fleet-ai-cron-mgr-panel";
describe("FleetAiCronMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCronMgrPanel managers={3} active={3} jobs={500} runs={15000} missed={0} />);
    expect(container.textContent).toContain("Cron Manager");
}); });
