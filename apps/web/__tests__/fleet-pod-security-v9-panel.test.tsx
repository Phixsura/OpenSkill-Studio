import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPodSecurityV9Panel } from "@/components/fleet-pod-security-v9-panel";
describe("FleetPodSecurityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPodSecurityV9Panel namespaces={30} restricted={20} />);
    expect(container.textContent).toContain("Pod Security v9");
}); });
