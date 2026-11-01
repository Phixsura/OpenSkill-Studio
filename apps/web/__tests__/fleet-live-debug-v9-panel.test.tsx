import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLiveDebugV9Panel } from "@/components/fleet-live-debug-v9-panel";
describe("FleetLiveDebugV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLiveDebugV9Panel sessions={10} breakpoints={25} />);
    expect(container.textContent).toContain("Live Debug v9");
}); });
