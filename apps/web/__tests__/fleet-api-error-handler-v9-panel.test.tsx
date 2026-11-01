import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiErrorHandlerV9Panel } from "@/components/fleet-api-error-handler-v9-panel";
describe("FleetApiErrorHandlerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiErrorHandlerV9Panel handlers={50} errors={500} />);
    expect(container.textContent).toContain("Error Handler v9");
}); });
