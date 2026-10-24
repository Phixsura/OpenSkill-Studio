import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGwPanel } from "@/components/fleet-ai-gw-panel";
describe("FleetAiGwPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGwPanel gateways={3} active={3} requests={3000000} cacheHitRate={45} tokensSaved={150000000} />);
    expect(container.textContent).toContain("AI Gateway");
}); });
