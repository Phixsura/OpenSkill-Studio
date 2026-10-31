import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInfProfPanel } from "@/components/fleet-ai-inf-prof-panel";
describe("FleetAiInfProfPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiInfProfPanel profilers={4} active={4} profiles={5000000} tokenizeMs={1} inferenceMs={30} />);
    expect(container.textContent).toContain("Inference Profiler");
}); });
