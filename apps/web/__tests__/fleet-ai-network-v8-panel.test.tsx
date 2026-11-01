import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNetworkV8Panel } from "@/components/fleet-ai-network-v8-panel";
describe("FleetAiNetworkV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiNetworkV8Panel systems={5} active={5} tbps={500} latency={0.5} regions={50} />);
    expect(container.textContent).toContain("Network v8");
}); });
