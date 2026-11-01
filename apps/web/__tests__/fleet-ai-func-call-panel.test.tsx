import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFuncCallPanel } from "@/components/fleet-ai-func-call-panel";
describe("FleetAiFuncCallPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFuncCallPanel services={10} active={10} calls={10000000} tools={100} successRate={99} />);
    expect(container.textContent).toContain("AI Function Calling");
}); });
