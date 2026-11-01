import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSamplingPanel } from "@/components/fleet-ai-sampling-panel";
describe("FleetAiSamplingPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSamplingPanel samplers={4} active={4} rate={5} sampled={50000000} saved={95} />);
    expect(container.textContent).toContain("AI Sampling");
}); });
