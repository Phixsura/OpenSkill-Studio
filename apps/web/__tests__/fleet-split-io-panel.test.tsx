import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSplitIoPanel } from "@/components/fleet-split-io-panel";
describe("FleetSplitIoPanel", () => { it("renders", () => {
    const { container } = render(<FleetSplitIoPanel total={50} active={45} withMetrics={40} treatments={100} />);
    expect(container.textContent).toContain("Split.io");
    expect(container.textContent).toContain("100 treatments");
}); });
