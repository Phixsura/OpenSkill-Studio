import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ConfigValidationCard from "../src/components/config-validation-card";

const validResult = {
  valid: true,
  errors: [],
  warnings: [],
  schema_id: "app-manifest-v1",
};

const invalidResult = {
  valid: false,
  errors: [
    { field: "port", message: "Value 0 below minimum 1", value: 0 },
    { field: "name", message: "Required field is missing" },
  ],
  warnings: ["Unknown field: extra"],
  schema_id: "app-manifest-v1",
};

const warningsOnly = {
  valid: true,
  errors: [],
  warnings: ["timeout: using default value", "Unknown field: legacy_mode"],
  schema_id: "webhook-config",
};

describe("ConfigValidationCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ConfigValidationCard result={validResult} appName="My App" />);
    expect(container.textContent).toContain("Config Validation");
    expect(container.textContent).toContain("My App");
  });

  it("shows schema id", () => {
    const { container } = render(<ConfigValidationCard result={validResult} appName="App" />);
    expect(container.textContent).toContain("app-manifest-v1");
  });

  it("shows valid badge when all good", () => {
    const { container } = render(<ConfigValidationCard result={validResult} appName="App" />);
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("All configuration fields are valid");
  });

  it("shows error count badge when invalid", () => {
    const { container } = render(<ConfigValidationCard result={invalidResult} appName="App" />);
    expect(container.textContent).toContain("2 errors");
  });

  it("renders error field names and messages", () => {
    const { container } = render(<ConfigValidationCard result={invalidResult} appName="App" />);
    expect(container.textContent).toContain("port");
    expect(container.textContent).toContain("Value 0 below minimum 1");
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("Required field is missing");
  });

  it("renders error value when present", () => {
    const { container } = render(<ConfigValidationCard result={invalidResult} appName="App" />);
    expect(container.textContent).toContain("Value: 0");
  });

  it("renders warnings", () => {
    const { container } = render(<ConfigValidationCard result={invalidResult} appName="App" />);
    expect(container.textContent).toContain("Warnings");
    expect(container.textContent).toContain("Unknown field: extra");
  });

  it("shows warnings without errors", () => {
    const { container } = render(<ConfigValidationCard result={warningsOnly} appName="App" />);
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("using default value");
    expect(container.textContent).not.toContain("All configuration fields are valid");
  });

  it("does not show errors section when valid", () => {
    const { container } = render(<ConfigValidationCard result={validResult} appName="App" />);
    expect(container.textContent).not.toContain("Errors");
  });
});
