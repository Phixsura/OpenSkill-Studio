import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSvcDiscPanel } from "@/components/fleet-ai-svc-disc-panel";
describe("FleetAiSvcDiscPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSvcDiscPanel registries={3} active={3} services={1000} instances={10000} lookups={500000000} />);
    expect(container.textContent).toContain("Service Discovery");
}); });
