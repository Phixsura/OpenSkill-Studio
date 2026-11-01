import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCultureV7Panel } from "@/components/fleet-ai-culture-v7-panel";
describe("FleetAiCultureV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCultureV7Panel trackers={3} active={3} enps={80} dx={95} hackathons={24} />);
    expect(container.textContent).toContain("Culture v7");
}); });
