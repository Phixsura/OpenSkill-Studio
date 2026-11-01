import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAirflowPanel } from "@/components/fleet-airflow-panel";
describe("FleetAirflowPanel", () => { it("renders", () => {
    const { container } = render(<FleetAirflowPanel environments={3} healthy={3} dags={300} activeRuns={50} failed={0} />);
    expect(container.textContent).toContain("Airflow");
    expect(container.textContent).toContain("300 DAGs");
}); });
