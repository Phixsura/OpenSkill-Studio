import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLoadTestPanel } from "@/components/fleet-ai-load-test-panel";
describe("FleetAiLoadTestPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLoadTestPanel testers={3} active={3} tests={100} maxRps={500000} p99={50} errorPct={0.05} />);
    expect(container.textContent).toContain("Load Test");
}); });
