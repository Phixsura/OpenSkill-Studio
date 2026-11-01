import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDoraV8Panel } from "@/components/fleet-ai-dora-v8-panel";
describe("FleetAiDoraV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDoraV8Panel freq={1000} lead={1} fail={0.01} mttr={1} cls="Elite" />);
    expect(container.textContent).toContain("DORA v8");
    expect(container.textContent).toContain("Elite");
}); });
