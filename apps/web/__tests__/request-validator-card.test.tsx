import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestValidatorCard from "../src/components/request-validator-card";

const issues = [
  { field: "name", message: "Required field missing" },
  { field: "age", message: "Below minimum (0)" },
];

describe("RequestValidatorCard", () => {
  it("renders header and schema id", () => {
    const { container } = render(
      <RequestValidatorCard
        schemaId="create_user"
        valid={false}
        issues={issues}
        fieldCount={5}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Request Validation");
    expect(container.textContent).toContain("create_user");
  });

  it("shows valid badge", () => {
    const { container } = render(
      <RequestValidatorCard schemaId="s1" valid={true} issues={[]} fieldCount={3} appName="App" />,
    );
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("All fields validated");
  });

  it("shows issue count badge", () => {
    const { container } = render(
      <RequestValidatorCard
        schemaId="s1"
        valid={false}
        issues={issues}
        fieldCount={5}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("2 issues");
  });

  it("renders issue fields and messages", () => {
    const { container } = render(
      <RequestValidatorCard
        schemaId="s1"
        valid={false}
        issues={issues}
        fieldCount={5}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("Required field missing");
    expect(container.textContent).toContain("age");
  });

  it("shows field count", () => {
    const { container } = render(
      <RequestValidatorCard schemaId="s1" valid={true} issues={[]} fieldCount={5} appName="App" />,
    );
    expect(container.textContent).toContain("5 fields");
  });
});
