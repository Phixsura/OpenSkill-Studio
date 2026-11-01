import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBluegreenPanel } from "@/components/fleet-bluegreen-panel";
describe("FleetBluegreenPanel", () => { it("renders", () => {
    const { container } = render(<FleetBluegreenPanel total={5} greenLive={3} blueLive={1} switching={1} stable={false} />);
    expect(container.textContent).toContain("Blue-Green");
    expect(container.textContent).toContain("1 switching");
}); });
