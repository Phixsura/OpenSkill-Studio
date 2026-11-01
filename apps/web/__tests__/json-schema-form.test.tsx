import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { JsonSchemaForm } from "@/components/json-schema-form";

describe("JsonSchemaForm", () => {
  const fields = [
    { name: "name", label: "App Name", type: "text", required: true, default: null, description: "Your app", enum: null, min: null, max: null },
    { name: "env", label: "Environment", type: "select", required: false, default: "dev", description: "", enum: ["dev", "prod"], min: null, max: null },
  ];
  it("renders fields", () => {
    const { container } = render(<JsonSchemaForm fields={fields} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("App Name");
    expect(container.textContent).toContain("Environment");
    expect(container.querySelector("input[name='name']")).toBeTruthy();
    expect(container.querySelector("select[name='env']")).toBeTruthy();
    expect(container.textContent).toContain("Submit");
  });
});
