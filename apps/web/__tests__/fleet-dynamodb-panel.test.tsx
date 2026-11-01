import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDynamodbPanel } from "@/components/fleet-dynamodb-panel";
describe("FleetDynamodbPanel", () => { it("renders", () => {
    const { container } = render(<FleetDynamodbPanel tables={20} active={20} throttled={2} consumedRcu={50000} />);
    expect(container.textContent).toContain("DynamoDB");
    expect(container.textContent).toContain("2 throttled");
}); });
