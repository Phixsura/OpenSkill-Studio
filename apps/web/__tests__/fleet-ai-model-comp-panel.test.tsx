import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCompPanel } from "@/components/fleet-ai-model-comp-panel";
describe("FleetAiModelCompPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCompPanel checkers={4} active={4} models={500} passed={498} failed={2} frameworks={15} />);
    expect(container.textContent).toContain("Model Compliance");
}); });
