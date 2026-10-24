import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEksPanel } from "@/components/fleet-eks-panel";
describe("FleetEksPanel", () => { it("renders", () => {
    const { container } = render(<FleetEksPanel clusters={5} active={5} fargateProfiles={5} managedNodegroups={10} />);
    expect(container.textContent).toContain("EKS");
    expect(container.textContent).toContain("5 Fargate");
}); });
