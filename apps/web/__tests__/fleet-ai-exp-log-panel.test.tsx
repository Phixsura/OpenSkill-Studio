import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExpLogPanel } from "@/components/fleet-ai-exp-log-panel";
describe("FleetAiExpLogPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExpLogPanel loggers={3} active={3} experiments={5000} runs={200000} artifacts={1000000} />);
    expect(container.textContent).toContain("Experiment Log");
}); });
