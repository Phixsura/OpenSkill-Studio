import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAppsyncPanel } from "@/components/fleet-appsync-panel";
describe("FleetAppsyncPanel", () => { it("renders", () => {
    const { container } = render(<FleetAppsyncPanel apis={5} active={5} requests={2000000} errors4xx={500} errors5xx={0} />);
    expect(container.textContent).toContain("AppSync");
    expect(container.textContent).toContain("2,000,000");
}); });
