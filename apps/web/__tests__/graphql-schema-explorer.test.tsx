import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GraphQLSchemaExplorer } from "@/components/graphql-schema-explorer";

const types = [
  { name: "User", kind: "type", description: "A user", fields: [{ name: "id", type: "ID!", description: "" }, { name: "name", type: "String!", description: "" }] },
  { name: "Query", kind: "type", description: "", fields: [{ name: "users", type: "[User]", description: "" }] },
];

describe("GraphQLSchemaExplorer", () => {
  it("renders types", () => {
    const { container } = render(<GraphQLSchemaExplorer types={types} />);
    expect(container.textContent).toContain("User");
    expect(container.textContent).toContain("Query");
    expect(container.textContent).toContain("2 types");
  });
  it("shows fields on click", () => {
    const { container } = render(<GraphQLSchemaExplorer types={types} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]); // User
    expect(container.textContent).toContain("ID!");
    expect(container.textContent).toContain("String!");
  });
});
