import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGcpDmPanel } from "@/components/fleet-gcp-dm-panel";
describe("FleetGcpDmPanel", () => { it("renders", () => {
    const { container } = render(<FleetGcpDmPanel total={10} done={9} failed={1} />);
    expect(container.textContent).toContain("GCP DM");
}); });
