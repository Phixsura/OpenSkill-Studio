import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetK8sOperatorV9Panel } from "@/components/fleet-k8s-operator-v9-panel";
describe("FleetK8sOperatorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetK8sOperatorV9Panel operators={5} reconciles={500} />);
    expect(container.textContent).toContain("K8s Operator v9");
}); });
