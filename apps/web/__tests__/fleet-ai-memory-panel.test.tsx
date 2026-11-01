import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMemoryPanel } from "@/components/fleet-ai-memory-panel";
describe("FleetAiMemoryPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMemoryPanel stores={5} active={5} memories={50000000} retrievals={25000000} />);
    expect(container.textContent).toContain("AI Memory");
}); });
