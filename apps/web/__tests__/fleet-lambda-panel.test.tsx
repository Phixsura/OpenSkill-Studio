import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLambdaPanel } from "@/components/fleet-lambda-panel";
describe("FleetLambdaPanel", () => { it("renders", () => {
    const { container } = render(<FleetLambdaPanel functions={50} active={50} invocations={20000000} errors={0} coldStart={3} />);
    expect(container.textContent).toContain("Lambda");
    expect(container.textContent).toContain("20,000,000");
}); });
