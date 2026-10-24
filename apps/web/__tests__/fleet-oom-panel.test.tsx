import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOomPanel } from "@/components/fleet-oom-panel";
describe("FleetOomPanel", () => { it("renders", () => {
    const { container } = render(<FleetOomPanel total={50} oomPods={2} totalOoms={5} healthy={false} />);
    expect(container.textContent).toContain("OOM Kills");
    expect(container.textContent).toContain("5 OOMs");
}); });
