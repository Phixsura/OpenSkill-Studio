import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPodLifecycleV9Panel } from "@/components/fleet-pod-lifecycle-v9-panel";
describe("FleetPodLifecycleV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPodLifecycleV9Panel pods={500} running={490} />);
    expect(container.textContent).toContain("Pod Lifecycle v9");
}); });
