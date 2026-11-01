import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOnboardPanel } from "@/components/fleet-ai-onboard-panel";
describe("FleetAiOnboardPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOnboardPanel wizards={3} active={3} completions={20000} avgMin={8} dropOff={10} />);
    expect(container.textContent).toContain("Onboarding");
}); });
