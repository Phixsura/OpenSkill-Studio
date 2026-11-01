import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpinnakerPanel } from "@/components/fleet-spinnaker-panel";
describe("FleetSpinnakerPanel", () => { it("renders", () => {
    const { container } = render(<FleetSpinnakerPanel total={30} succeeded={25} failed={3} running={2} successRate={83.3} />);
    expect(container.textContent).toContain("Spinnaker");
    expect(container.textContent).toContain("83.3% success");
}); });
