import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCommunityPanel } from "@/components/fleet-ai-community-panel";
describe("FleetAiCommunityPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCommunityPanel forums={2} active={2} members={200000} posts={2000} resolved={90} />);
    expect(container.textContent).toContain("AI Community");
}); });
