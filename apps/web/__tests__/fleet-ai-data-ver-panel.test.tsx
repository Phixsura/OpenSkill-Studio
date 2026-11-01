import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataVerPanel } from "@/components/fleet-ai-data-ver-panel";
describe("FleetAiDataVerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataVerPanel systems={3} active={3} datasets={500} versions={5000} storageTb={100} />);
    expect(container.textContent).toContain("Data Versioning");
}); });
