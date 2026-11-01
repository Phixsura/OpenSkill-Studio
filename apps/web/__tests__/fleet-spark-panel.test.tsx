import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSparkPanel } from "@/components/fleet-spark-panel";
describe("FleetSparkPanel", () => { it("renders", () => {
    const { container } = render(<FleetSparkPanel clusters={5} running={5} executors={200} activeJobs={30} />);
    expect(container.textContent).toContain("Spark");
    expect(container.textContent).toContain("200 executors");
}); });
