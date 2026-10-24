import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlaygroundPanel } from "@/components/fleet-ai-playground-panel";
describe("FleetAiPlaygroundPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlaygroundPanel instances={5} active={5} sessions={200000} prompts={2000000} />);
    expect(container.textContent).toContain("AI Playground");
}); });
