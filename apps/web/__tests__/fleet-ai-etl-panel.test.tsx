import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEtlPanel } from "@/components/fleet-ai-etl-panel";
describe("FleetAiEtlPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEtlPanel engines={4} active={4} jobs={1000} records={500000000} failures={0} />);
    expect(container.textContent).toContain("ETL Engine");
}); });
