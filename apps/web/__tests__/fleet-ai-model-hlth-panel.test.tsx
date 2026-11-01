import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelHlthPanel } from "@/components/fleet-ai-model-hlth-panel";
describe("FleetAiModelHlthPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelHlthPanel checkers={4} active={4} models={200} healthy={198} degraded={2} score={97} />);
    expect(container.textContent).toContain("Model Health");
}); });
