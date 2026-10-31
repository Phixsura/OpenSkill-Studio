import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTraceSamplingV9Panel } from "@/components/fleet-trace-sampling-v9-panel";
describe("FleetTraceSamplingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTraceSamplingV9Panel strategies={5} rate={10} />);
    expect(container.textContent).toContain("Trace Sampling v9");
}); });
