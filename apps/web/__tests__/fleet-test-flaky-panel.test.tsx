import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTestFlakyPanel } from "@/components/fleet-test-flaky-panel";
describe("FleetTestFlakyPanel", () => { it("renders", () => {
    const { container } = render(<FleetTestFlakyPanel total={1000} flaky={50} flakyRate={5} acceptable={false} />);
    expect(container.textContent).toContain("Test Flakiness");
    expect(container.textContent).toContain("Too many flaky");
}); });
