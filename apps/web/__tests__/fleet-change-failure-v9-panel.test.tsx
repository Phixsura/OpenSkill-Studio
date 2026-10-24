import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChangeFailureV9Panel } from "@/components/fleet-change-failure-v9-panel";
describe("FleetChangeFailureV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetChangeFailureV9Panel deployments={1000} cfr={0.5} />);
    expect(container.textContent).toContain("Change Failure v9");
}); });
