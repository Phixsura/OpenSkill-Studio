import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGoldenSignalV9Panel } from "@/components/fleet-golden-signal-v9-panel";
describe("FleetGoldenSignalV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGoldenSignalV9Panel services={50} allOk={true} />);
    expect(container.textContent).toContain("Golden Signals v9");
}); });
