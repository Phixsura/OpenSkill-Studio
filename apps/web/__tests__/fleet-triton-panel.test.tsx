import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTritonPanel } from "@/components/fleet-triton-panel";
describe("FleetTritonPanel", () => { it("renders", () => {
    const { container } = render(<FleetTritonPanel servers={10} ready={10} modelsLoaded={50} inferencesPerSec={250000} />);
    expect(container.textContent).toContain("Triton");
}); });
