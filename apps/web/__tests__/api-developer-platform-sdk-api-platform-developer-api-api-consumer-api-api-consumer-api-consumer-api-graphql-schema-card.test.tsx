import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-graphql-schema-card";

describe("ConsumerApiGraphqlSchemaCard", () => {
  it("shows types and fields", () => {
    const types = [{ name: "User", kind: "object", fields: [{ name: "id", type: "ID", deprecated: false }, { name: "email", type: "String", deprecated: false }] }];
    const { container } = render(<Card types={types} appName="App" />);
    expect(container.textContent).toContain("GraphQL Schema");
    expect(container.textContent).toContain("User");
    expect(container.textContent).toContain("object");
    expect(container.textContent).toContain("id: ID");
  });
  it("shows empty", () => {
    const { container } = render(<Card types={[]} appName="App" />);
    expect(container.textContent).toContain("No types registered");
  });
});
