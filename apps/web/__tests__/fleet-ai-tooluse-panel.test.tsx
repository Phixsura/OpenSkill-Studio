import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiToolusePanel } from "@/components/fleet-ai-tooluse-panel";
describe("FleetAiToolusePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiToolusePanel services={10} active={10} toolCalls={25000000} tools={200} successRate={98} />);
    expect(container.textContent).toContain("AI Tool Use");
}); });
