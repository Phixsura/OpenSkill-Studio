import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOnboardingPanel } from "@/components/fleet-onboarding-panel";
describe("FleetOnboardingPanel", () => { it("renders", () => {
    const { container } = render(<FleetOnboardingPanel total={10} onboarded={8} pending={2} avgDays={4} fast={true} />);
    expect(container.textContent).toContain("Developer Onboarding");
    expect(container.textContent).toContain("2 pending");
}); });
