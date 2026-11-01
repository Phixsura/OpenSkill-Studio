import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSecPosturePanel } from "@/components/fleet-sec-posture-panel";
describe("FleetSecPosturePanel", () => { it("renders", () => {
    const { container } = render(<FleetSecPosturePanel score={95} grade="A" criticalFails={0} />);
    expect(container.textContent).toContain("Security Posture");
    expect(container.textContent).toContain("95% — A");
}); });
