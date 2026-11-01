import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEtcdPanel } from "@/components/fleet-etcd-panel";
describe("FleetEtcdPanel", () => { it("renders", () => {
    const { container } = render(<FleetEtcdPanel members={3} healthy={3} totalKeys={30000} dbSizeMb={300} quorum={true} />);
    expect(container.textContent).toContain("etcd Health");
    expect(container.textContent).toContain("Quorum");
}); });
