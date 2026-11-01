import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTestRunnerV9Panel } from "@/components/fleet-test-runner-v9-panel";
describe("FleetTestRunnerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTestRunnerV9Panel suites={50} passed={5000} />);
    expect(container.textContent).toContain("Test Runner v9");
}); });
