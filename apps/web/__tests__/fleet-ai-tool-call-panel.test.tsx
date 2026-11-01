import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiToolCallPanel } from "@/components/fleet-ai-tool-call-panel";
describe("FleetAiToolCallPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiToolCallPanel services={5} active={5} tools={500} calls={5000000} latency={18} />);
    expect(container.textContent).toContain("Tool Calling");
}); });
