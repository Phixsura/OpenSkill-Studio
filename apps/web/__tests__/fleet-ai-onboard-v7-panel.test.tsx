import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOnboardV7Panel } from "@/components/fleet-ai-onboard-v7-panel";
describe("FleetAiOnboardV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiOnboardV7Panel systems={3} active={3} completions={200000} ttfv={3} drop={8} />);
    expect(container.textContent).toContain("Onboarding v7");
}); });
