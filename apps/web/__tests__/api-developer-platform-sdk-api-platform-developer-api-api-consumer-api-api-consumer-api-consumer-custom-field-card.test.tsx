import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-custom-field-card";

describe("ConsumerCustomFieldCard", () => {
  it("shows fields", () => {
    const fields = [{ name: "company", value: "Acme Inc", type: "string" }, { name: "tier", value: "pro", type: "string" }];
    const { container } = render(<Card fields={fields} consumerId="c1" maxFields={50} appName="App" />);
    expect(container.textContent).toContain("Custom Fields");
    expect(container.textContent).toContain("company");
    expect(container.textContent).toContain("Acme Inc");
    expect(container.textContent).toContain("2/50 fields");
  });
  it("shows empty", () => {
    const { container } = render(<Card fields={[]} consumerId="c1" maxFields={50} appName="App" />);
    expect(container.textContent).toContain("No custom fields");
  });
});
