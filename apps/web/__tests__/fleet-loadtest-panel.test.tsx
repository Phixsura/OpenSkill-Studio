import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLoadtestPanel } from "@/components/fleet-loadtest-panel";
describe("FleetLoadtestPanel", () => { it("renders", () => {
    const { container } = render(<FleetLoadtestPanel total={5} passed={4} maxRps={10000} avgP99={300} allPassed={false} />);
    expect(container.textContent).toContain("Load Tests");
    expect(container.textContent).toContain("Some tests failed");
}); });
