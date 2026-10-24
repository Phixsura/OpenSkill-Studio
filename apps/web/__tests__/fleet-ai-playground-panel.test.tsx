import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlaygroundPanel } from "@/components/fleet-ai-playground-panel";
describe("FleetAiPlaygroundPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlaygroundPanel playgrounds={5} active={5} users={200000} experiments={1000000} models={50} />);
    expect(container.textContent).toContain("AI Playground");
}); });
