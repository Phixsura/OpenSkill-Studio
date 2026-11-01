import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetK8sAdmissionV9Panel } from "@/components/fleet-k8s-admission-v9-panel";
describe("FleetK8sAdmissionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetK8sAdmissionV9Panel webhooks={10} denied={5} />);
    expect(container.textContent).toContain("K8s Admission v9");
}); });
