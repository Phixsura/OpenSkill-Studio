import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExpVerPanel } from "@/components/fleet-ai-exp-ver-panel";
describe("FleetAiExpVerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExpVerPanel systems={3} active={3} experiments={1000} snapshots={10000} reproducible={99} />);
    expect(container.textContent).toContain("Experiment Versioning");
}); });
