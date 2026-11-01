import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWorkloadIdentityV9Panel } from "@/components/fleet-workload-identity-v9-panel";
describe("FleetWorkloadIdentityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWorkloadIdentityV9Panel workloads={200} federated={200} />);
    expect(container.textContent).toContain("Workload Identity v9");
}); });
