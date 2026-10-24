import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCommunityV7Panel } from "@/components/fleet-ai-community-v7-panel";
describe("FleetAiCommunityV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCommunityV7Panel systems={3} active={3} members={2000000} contributors={20000} discussions={200000} />);
    expect(container.textContent).toContain("Community v7");
}); });
