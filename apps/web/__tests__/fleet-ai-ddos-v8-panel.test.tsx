import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDdosV8Panel } from "@/components/fleet-ai-ddos-v8-panel";
describe("FleetAiDdosV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDdosV8Panel systems={5} active={5} attacks={5000} peak={100} uptime={99.9999} />);
    expect(container.textContent).toContain("DDoS v8");
}); });
