import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLeadershipV7Panel } from "@/components/fleet-ai-leadership-v7-panel";
describe("FleetAiLeadershipV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiLeadershipV7Panel trackers={3} active={3} rank={1} awards={100} rating={4.95} />);
    expect(container.textContent).toContain("Leadership v7");
}); });
