import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPulumiPanel } from "@/components/fleet-pulumi-panel";
describe("FleetPulumiPanel", () => { it("renders", () => {
    const { container } = render(<FleetPulumiPanel total={10} upToDate={8} pending={1} failed={1} healthy={false} />);
    expect(container.textContent).toContain("Pulumi");
    expect(container.textContent).toContain("1 failed");
}); });
