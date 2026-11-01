import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCdnV8Panel } from "@/components/fleet-ai-cdn-v8-panel";
describe("FleetAiCdnV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCdnV8Panel cdns={5} active={5} pops={1000} pbps={50} hitPct={99} />);
    expect(container.textContent).toContain("CDN v8");
}); });
