import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPersonalPanel } from "@/components/fleet-ai-personal-panel";
describe("FleetAiPersonalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPersonalPanel engines={5} active={5} requests={100000000} engagementLift={30} />);
    expect(container.textContent).toContain("AI Personalization");
}); });
