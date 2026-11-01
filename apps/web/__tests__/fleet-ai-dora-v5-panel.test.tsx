import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDoraV5Panel } from "@/components/fleet-ai-dora-v5-panel";
describe("FleetAiDoraV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDoraV5Panel freq={500} lead={1} fail={0.05} mttr={3} cls="Elite" />);
    expect(container.textContent).toContain("DORA v5");
    expect(container.textContent).toContain("Elite");
}); });
