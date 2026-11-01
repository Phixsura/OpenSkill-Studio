import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDeveloperOnboardingV9Panel } from "@/components/fleet-api-developer-onboarding-v9-panel";
describe("FleetApiDeveloperOnboardingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDeveloperOnboardingV9Panel devs={500} onboarded={480} />);
    expect(container.textContent).toContain("Dev Onboarding v9");
}); });
