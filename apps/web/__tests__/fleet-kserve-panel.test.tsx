import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKservePanel } from "@/components/fleet-kserve-panel";
describe("FleetKservePanel", () => { it("renders", () => {
    const { container } = render(<FleetKservePanel services={10} ready={10} models={50} qps={50000} />);
    expect(container.textContent).toContain("KServe");
}); });
