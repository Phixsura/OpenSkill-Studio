import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMlflowPanel } from "@/components/fleet-mlflow-panel";
describe("FleetMlflowPanel", () => { it("renders", () => {
    const { container } = render(<FleetMlflowPanel servers={3} running={3} experiments={200} runs={10000} models={100} />);
    expect(container.textContent).toContain("MLflow");
}); });
