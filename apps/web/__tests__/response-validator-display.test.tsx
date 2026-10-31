import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResponseValidatorDisplay } from "@/components/response-validator-display";

describe("ResponseValidatorDisplay", () => {
  it("renders valid", () => {
    const { container } = render(
      <ResponseValidatorDisplay valid={true} errors={[]} responseType="single"
        statusCode={200} statusIssues={[]} />
    );
    expect(container.textContent).toContain("Response Validator");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("Valid");
  });

  it("renders errors", () => {
    const { container } = render(
      <ResponseValidatorDisplay valid={false} errors={["Missing 'data'"]}
        responseType="single" statusCode={400} statusIssues={["Should have error body"]} />
    );
    expect(container.textContent).toContain("2 issues");
    expect(container.textContent).toContain("Missing 'data'");
  });
});
