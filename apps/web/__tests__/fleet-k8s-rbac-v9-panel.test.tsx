import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetK8sRbacV9Panel } from "@/components/fleet-k8s-rbac-v9-panel";
describe("FleetK8sRbacV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetK8sRbacV9Panel roles={30} overPrivileged={0} />);
    expect(container.textContent).toContain("K8s RBAC v9");
}); });
