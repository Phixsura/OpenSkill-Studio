import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStepfnPanel } from "@/components/fleet-stepfn-panel";
describe("FleetStepfnPanel", () => { it("renders", () => {
    const { container } = render(<FleetStepfnPanel machines={10} active={10} running={50} succeeded={5000} failed={0} />);
    expect(container.textContent).toContain("Step Functions");
}); });
