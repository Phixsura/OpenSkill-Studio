import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMoePanel } from "@/components/fleet-ai-moe-panel";
describe("FleetAiMoePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMoePanel routers={3} active={3} experts={128} tokens={200000000000} loadBalance={0.97} />);
    expect(container.textContent).toContain("Mixture of Experts");
}); });
