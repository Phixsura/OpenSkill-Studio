import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSecV6Panel } from "@/components/fleet-ai-sec-v6-panel";
describe("FleetAiSecV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSecV6Panel systems={5} active={5} score={99} threats={50000} zt={true} />);
    expect(container.textContent).toContain("Security v6");
}); });
