import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlayV3Panel } from "@/components/fleet-ai-play-v3-panel";
describe("FleetAiPlayV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlayV3Panel playgrounds={3} active={3} sessions={500000} collaborators={1000} notebooks={5000} />);
    expect(container.textContent).toContain("Playground v3");
}); });
