import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSecurityPostureV9Panel } from "@/components/fleet-api-security-posture-v9-panel";
describe("FleetApiSecurityPostureV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSecurityPostureV9Panel apis={200} score={95} />);
    expect(container.textContent).toContain("API Security Posture v9");
}); });
