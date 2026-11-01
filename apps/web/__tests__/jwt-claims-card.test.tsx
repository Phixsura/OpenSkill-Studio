import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import JWTClaimsCard from "../src/components/jwt-claims-card";

const validJWT = {
  valid: true,
  claims: { sub: "user-1", iss: "https://auth.example.com", exp: 9999999999 },
  errors: [],
  issuer: "https://auth.example.com",
  audience: "my-app",
  expired: false,
};

const invalidJWT = {
  valid: false,
  claims: { sub: "user-1" },
  errors: ["Missing required claim: email", "Token expired"],
  issuer: "",
  audience: "",
  expired: true,
};

describe("JWTClaimsCard", () => {
  it("renders header", () => {
    const { container } = render(<JWTClaimsCard validation={validJWT} appName="My App" />);
    expect(container.textContent).toContain("JWT Claims");
  });

  it("shows valid badge", () => {
    const { container } = render(<JWTClaimsCard validation={validJWT} appName="App" />);
    expect(container.textContent).toContain("Valid");
  });

  it("shows invalid badge", () => {
    const { container } = render(<JWTClaimsCard validation={invalidJWT} appName="App" />);
    expect(container.textContent).toContain("Invalid");
  });

  it("renders errors", () => {
    const { container } = render(<JWTClaimsCard validation={invalidJWT} appName="App" />);
    expect(container.textContent).toContain("Missing required claim: email");
    expect(container.textContent).toContain("Token expired");
  });

  it("renders claims", () => {
    const { container } = render(<JWTClaimsCard validation={validJWT} appName="App" />);
    expect(container.textContent).toContain("sub");
    expect(container.textContent).toContain("user-1");
    expect(container.textContent).toContain("iss");
  });
});
