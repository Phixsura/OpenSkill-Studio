import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSagemakerPanel } from "@/components/fleet-sagemaker-panel";
describe("FleetSagemakerPanel", () => { it("renders", () => {
    const { container } = render(<FleetSagemakerPanel endpoints={10} inService={10} instances={40} invocations={2000000} />);
    expect(container.textContent).toContain("SageMaker");
}); });
