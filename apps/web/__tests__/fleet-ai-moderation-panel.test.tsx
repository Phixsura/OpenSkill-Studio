import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModerationPanel } from "@/components/fleet-ai-moderation-panel";
describe("FleetAiModerationPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModerationPanel services={5} active={5} items={50000000} flagged={250000} flagRate={0.5} />);
    expect(container.textContent).toContain("AI Moderation");
}); });
