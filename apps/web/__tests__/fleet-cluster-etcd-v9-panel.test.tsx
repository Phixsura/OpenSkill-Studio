import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterEtcdV9Panel } from "@/components/fleet-cluster-etcd-v9-panel";
describe("FleetClusterEtcdV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterEtcdV9Panel clusters={5} dbSize={500} />);
    expect(container.textContent).toContain("Cluster etcd v9");
}); });
