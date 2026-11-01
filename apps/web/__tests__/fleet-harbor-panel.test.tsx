import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHarborPanel } from "@/components/fleet-harbor-panel";
describe("FleetHarborPanel", () => { it("renders", () => {
    const { container } = render(<FleetHarborPanel projects={10} repos={80} artifacts={1000} overQuota={1} healthy={false} />);
    expect(container.textContent).toContain("Harbor");
    expect(container.textContent).toContain("1 over quota");
}); });
