import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGraphqlGatewayV9Panel } from "@/components/fleet-graphql-gateway-v9-panel";
describe("FleetGraphqlGatewayV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGraphqlGatewayV9Panel endpoints={5} qps={5000} />);
    expect(container.textContent).toContain("GraphQL Gateway v9");
}); });
