import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTidbPanel } from "@/components/fleet-tidb-panel";
describe("FleetTidbPanel", () => { it("renders", () => {
    const { container } = render(<FleetTidbPanel clusters={3} healthy={3} tikvStores={27} qps={300000} />);
    expect(container.textContent).toContain("TiDB");
    expect(container.textContent).toContain("27 TiKV");
}); });
