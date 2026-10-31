import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGraphqlPanel } from "@/components/fleet-graphql-panel";
describe("FleetGraphqlPanel", () => { it("renders", () => {
    const { container } = render(<FleetGraphqlPanel total={100} slowQueries={5} deepQueries={3} avgDuration={350} healthy={false} />);
    expect(container.textContent).toContain("GraphQL");
    expect(container.textContent).toContain("Slow queries");
}); });
