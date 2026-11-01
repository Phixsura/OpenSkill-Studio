import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidatorCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-request-body-validator-card";

describe("Card", () => {
  it("shows validator stats", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidatorCard stats={{ total: 10000, invalid: 500 }} ruleCount={25} appName="App" />);
    expect(container.textContent).toContain("Body Validator");
    expect(container.textContent).toContain("25 rules");
    expect(container.textContent).toContain("10000");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("95%");
  });
});
