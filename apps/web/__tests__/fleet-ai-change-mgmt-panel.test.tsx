import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChangeMgmtPanel } from "@/components/fleet-ai-change-mgmt-panel";
describe("FleetAiChangeMgmtPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChangeMgmtPanel systems={2} active={2} changes={100} approved={95} rejected={5} />);
    expect(container.textContent).toContain("Change Management");
}); });
