import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGraphqlSubscriptionV9Panel } from "@/components/fleet-api-graphql-subscription-v9-panel";
describe("FleetApiGraphqlSubscriptionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGraphqlSubscriptionV9Panel subs={50} connections={5000} />);
    expect(container.textContent).toContain("GraphQL Sub v9");
}); });
