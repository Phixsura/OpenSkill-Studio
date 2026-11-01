import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-playground-template-card";

describe("PlaygroundTemplateCard", () => {
  it("shows templates", () => {
    const templates = [{ template_id: "t1", name: "Create User", method: "POST", path: "/users", category: "crud", usage_count: 42 }];
    const { container } = render(<Card templates={templates} categories={["crud"]} appName="App" />);
    expect(container.textContent).toContain("Playground Templates");
    expect(container.textContent).toContain("Create User");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("42× used");
  });
  it("shows empty", () => {
    const { container } = render(<Card templates={[]} categories={[]} appName="App" />);
    expect(container.textContent).toContain("No templates");
  });
});
