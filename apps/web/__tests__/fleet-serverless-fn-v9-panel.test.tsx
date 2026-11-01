import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServerlessFnV9Panel } from "@/components/fleet-serverless-fn-v9-panel";
describe("FleetServerlessFnV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServerlessFnV9Panel functions={50} invocations={50000} />);
    expect(container.textContent).toContain("Serverless v9");
}); });
