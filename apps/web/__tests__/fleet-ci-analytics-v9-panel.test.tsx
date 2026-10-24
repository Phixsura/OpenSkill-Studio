import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCiAnalyticsV9Panel } from "@/components/fleet-ci-analytics-v9-panel";
describe("FleetCiAnalyticsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCiAnalyticsV9Panel pipelines={20} successRate={99} />);
    expect(container.textContent).toContain("CI Analytics v9");
}); });
