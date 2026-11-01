import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlayV2Panel } from "@/components/fleet-ai-play-v2-panel";
describe("FleetAiPlayV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlayV2Panel playgrounds={5} active={5} sessions={500000} shared={100000} satisfaction={4.9} />);
    expect(container.textContent).toContain("Playground v2");
}); });
