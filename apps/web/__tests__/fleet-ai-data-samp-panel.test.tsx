import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataSampPanel } from "@/components/fleet-ai-data-samp-panel";
describe("FleetAiDataSampPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataSampPanel samplers={3} active={3} sampled={50000000} strategies={5} repr={97} />);
    expect(container.textContent).toContain("Data Sampler");
}); });
