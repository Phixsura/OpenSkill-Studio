import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatGwPanel } from "@/components/fleet-ai-plat-gw-panel";
describe("FleetAiPlatGwPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatGwPanel gateways={3} active={3} routes={1000} requests={2000000000} p99={10} />);
    expect(container.textContent).toContain("Platform Gateway");
}); });
