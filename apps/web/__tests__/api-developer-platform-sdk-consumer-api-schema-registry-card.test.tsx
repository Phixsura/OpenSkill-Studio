import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SchemaRegistryCard from "../src/components/api-developer-platform-sdk-consumer-api-schema-registry-card";

describe("SchemaRegistryCard", () => {
  it("renders title and schemas", () => {
    const { container } = render(<SchemaRegistryCard />);
    expect(container.textContent).toContain("Schema Registry");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows count", () => {
    const { container } = render(<SchemaRegistryCard />);
    expect(container.textContent).toContain("3 schemas registered");
  });
});
