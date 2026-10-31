import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLongCtxPanel } from "@/components/fleet-ai-long-ctx-panel";
describe("FleetAiLongCtxPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLongCtxPanel managers={3} active={3} maxTokens={1000000} utilization={75} requests={2000000} />);
    expect(container.textContent).toContain("Long Context");
}); });
