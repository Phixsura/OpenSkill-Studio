import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOnboardingV9Panel } from "@/components/fleet-onboarding-v9-panel";
describe("FleetOnboardingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetOnboardingV9Panel total={20} avgDays={5} />);
    expect(container.textContent).toContain("Onboarding v9");
}); });
