import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshRetryPanel } from "@/components/fleet-mesh-retry-panel";
describe("FleetMeshRetryPanel", () => { it("renders", () => {
    const { container } = render(<FleetMeshRetryPanel requests={3000} retries={350} retryRate={11.67} excessive={true} />);
    expect(container.textContent).toContain("Mesh Retries");
    expect(container.textContent).toContain("Excessive retries");
}); });
