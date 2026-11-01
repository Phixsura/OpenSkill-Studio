import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiPayloadSchemaValidatorCard from "../src/components/api-developer-api-api-payload-schema-validator-card";

const schemas = [
  { schema_id: "user", fields: [{ name: "email", field_type: "email", required: true }, { name: "bio", field_type: "string", required: false }] },
];

describe("APIDeveloperAPIApiPayloadSchemaValidatorCard", () => {
  it("shows schemas", () => {
    const { container } = render(<APIDeveloperAPIApiPayloadSchemaValidatorCard schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Schema Validator");
    expect(container.textContent).toContain("user");
    expect(container.textContent).toContain("email: email*");
    expect(container.textContent).toContain("bio: string");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiPayloadSchemaValidatorCard schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No schemas");
  });
});
