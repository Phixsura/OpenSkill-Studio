import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMcpPanel } from "@/components/fleet-ai-mcp-panel";
describe("FleetAiMcpPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMcpPanel servers={10} running={10} tools={200} resources={500} calls={10000000} />);
    expect(container.textContent).toContain("AI MCP");
}); });
