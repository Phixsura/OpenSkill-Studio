import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTraceSamplerPanel } from "@/components/fleet-trace-sampler-panel";
describe("FleetTraceSamplerPanel", () => { it("renders", () => {
    const { container } = render(<FleetTraceSamplerPanel totalSpans={15000} sampledPerSec={150} sampleRate={1} adequate={true} />);
    expect(container.textContent).toContain("Trace Sampling");
    expect(container.textContent).toContain("1% rate");
}); });
