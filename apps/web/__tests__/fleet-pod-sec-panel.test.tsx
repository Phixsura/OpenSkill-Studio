import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPodSecPanel } from "@/components/fleet-pod-sec-panel";
describe("FleetPodSecPanel", () => { it("renders", () => {
    const { container } = render(<FleetPodSecPanel total={20} privileged={2} runAsRoot={3} compliant={false} />);
    expect(container.textContent).toContain("Pod Security");
    expect(container.textContent).toContain("2 privileged");
}); });
