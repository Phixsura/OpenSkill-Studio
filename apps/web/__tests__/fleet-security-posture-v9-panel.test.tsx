import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSecurityPostureV9Panel } from "@/components/fleet-security-posture-v9-panel";
describe("FleetSecurityPostureV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSecurityPostureV9Panel domains={8} score={95} />);
    expect(container.textContent).toContain("Security Posture v9");
}); });
