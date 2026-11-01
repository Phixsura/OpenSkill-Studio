import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ContractValidatorCard from "../src/components/api-developer-platform-sdk-consumer-api-contract-validator-card";

describe("ContractValidatorCard", () => {
  it("renders title and contracts", () => {
    const { container } = render(<ContractValidatorCard />);
    expect(container.textContent).toContain("Contract Validator");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows pass rates and count", () => {
    const { container } = render(<ContractValidatorCard />);
    expect(container.textContent).toContain("99.2%");
    expect(container.textContent).toContain("3 contracts registered");
  });
});
