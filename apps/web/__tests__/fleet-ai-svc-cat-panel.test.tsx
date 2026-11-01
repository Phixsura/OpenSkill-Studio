import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSvcCatPanel } from "@/components/fleet-ai-svc-cat-panel";
describe("FleetAiSvcCatPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSvcCatPanel catalogs={2} active={2} services={500} owners={80} documented={97} />);
    expect(container.textContent).toContain("Service Catalog");
}); });
