import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTogetherPanel } from "@/components/fleet-together-panel";
describe("FleetTogetherPanel", () => { it("renders", () => {
    const { container } = render(<FleetTogetherPanel models={15} deployed={15} inferences={5000000} gpuHours={2000} />);
    expect(container.textContent).toContain("Together AI");
}); });
