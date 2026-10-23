import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigSchemaEditor } from "@/components/config-schema-editor";

describe("ConfigSchemaEditor", () => {
  const fields = [
    { name: "api_key", type: "secret", label: "Api Key", required: true, default: null, description: "Your key", options: null },
    { name: "debug", type: "boolean", label: "Debug", required: false, default: false, description: "", options: null },
  ];
  it("renders schema", () => {
    const { container } = render(<ConfigSchemaEditor fields={fields} errors={[]} valid={true} />);
    expect(container.textContent).toContain("api_key");
    expect(container.textContent).toContain("secret");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("2 fields");
  });
});
