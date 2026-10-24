import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataQualPanel } from "@/components/fleet-ai-data-qual-panel";
describe("FleetAiDataQualPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataQualPanel monitors={5} active={5} datasets={1000} checks={200000} quality={98} />);
    expect(container.textContent).toContain("Data Quality");
}); });
