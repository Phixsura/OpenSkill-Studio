import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiConnPoolPanel } from "@/components/fleet-ai-conn-pool-panel";
describe("FleetAiConnPoolPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiConnPoolPanel pools={8} active={8} max={5000} activeConns={3000} utilization={60} />);
    expect(container.textContent).toContain("Connection Pool");
}); });
