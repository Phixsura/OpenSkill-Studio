import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBuildBuyPanel } from "@/components/fleet-build-buy-panel";
describe("FleetBuildBuyPanel", () => { it("renders", () => {
    const { container } = render(<FleetBuildBuyPanel total={20} built={10} bought={5} oss={5} buildRatio={50} />);
    expect(container.textContent).toContain("Build vs Buy");
    expect(container.textContent).toContain("50% built");
}); });
