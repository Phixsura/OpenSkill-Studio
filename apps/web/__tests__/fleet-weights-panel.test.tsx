import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWeightsPanel } from "@/components/fleet-weights-panel";
describe("FleetWeightsPanel", () => { it("renders", () => {
    const { container } = render(<FleetWeightsPanel registries={5} active={5} models={200} versions={1000} storageTb={50} />);
    expect(container.textContent).toContain("Model Weights");
}); });
