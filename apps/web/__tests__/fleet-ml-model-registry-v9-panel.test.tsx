import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMlModelRegistryV9Panel } from "@/components/fleet-ml-model-registry-v9-panel";
describe("FleetMlModelRegistryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMlModelRegistryV9Panel models={50} deployed={30} />);
    expect(container.textContent).toContain("ML Model Registry v9");
}); });
