import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSidecarInjectorV9Panel } from "@/components/fleet-sidecar-injector-v9-panel";
describe("FleetSidecarInjectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSidecarInjectorV9Panel namespaces={10} pods={500} />);
    expect(container.textContent).toContain("Sidecar Injector v9");
}); });
