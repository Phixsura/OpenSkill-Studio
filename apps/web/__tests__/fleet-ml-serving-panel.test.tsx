import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMlServingPanel } from "@/components/fleet-ml-serving-panel";
describe("FleetMlServingPanel", () => { it("renders", () => {
    const { container } = render(<FleetMlServingPanel models={10} totalQps={5000} avgP99={45} staleModels={2} performant={true} />);
    expect(container.textContent).toContain("ML Serving");
    expect(container.textContent).toContain("2 stale");
}); });
