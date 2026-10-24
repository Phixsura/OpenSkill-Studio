import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDevExperienceV9Panel } from "@/components/fleet-api-dev-experience-v9-panel";
describe("FleetApiDevExperienceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDevExperienceV9Panel metrics={10} satisfaction={92} />);
    expect(container.textContent).toContain("API DevX v9");
}); });
