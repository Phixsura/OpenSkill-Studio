import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataGovV7Panel } from "@/components/fleet-ai-data-gov-v7-panel";
describe("FleetAiDataGovV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataGovV7Panel systems={3} active={3} datasets={50000} classified={50000} policies={500} compliance={99.8} />);
    expect(container.textContent).toContain("Data Gov v7");
}); });
