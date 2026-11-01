import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTokCountPanel } from "@/components/fleet-ai-tok-count-panel";
describe("FleetAiTokCountPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTokCountPanel counters={6} active={6} inputTokens={200000000000} outputTokens={40000000000} cost={60000} />);
    expect(container.textContent).toContain("Token Counter");
}); });
