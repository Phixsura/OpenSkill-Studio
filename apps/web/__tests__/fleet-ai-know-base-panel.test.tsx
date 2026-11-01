import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiKnowBasePanel } from "@/components/fleet-ai-know-base-panel";
describe("FleetAiKnowBasePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiKnowBasePanel bases={3} active={3} articles={50000} searches={2000000} helpful={95} />);
    expect(container.textContent).toContain("Knowledge Base");
}); });
