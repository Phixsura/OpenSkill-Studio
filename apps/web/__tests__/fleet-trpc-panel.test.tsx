import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrpcPanel } from "@/components/fleet-trpc-panel";
describe("FleetTrpcPanel", () => { it("renders", () => {
    const { container } = render(<FleetTrpcPanel routers={10} procedures={200} calls={2000000} errors={0} />);
    expect(container.textContent).toContain("tRPC");
    expect(container.textContent).toContain("200 procedures");
}); });
