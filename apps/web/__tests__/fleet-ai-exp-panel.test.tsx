import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExpPanel } from "@/components/fleet-ai-exp-panel";
describe("FleetAiExpPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExpPanel total={10} active={5} variants={15} avgTraffic={30} />);
    expect(container.textContent).toContain("AI Experiments");
}); });
