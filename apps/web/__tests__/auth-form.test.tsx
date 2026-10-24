import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AuthForm } from "@/components/auth-form";

describe("AuthForm", () => {
  it("login mode", () => {
    const { container } = render(
      <AuthForm mode="login" providers={[{ id: "github", label: "GitHub", icon: "🐙" }]}
        onSubmit={vi.fn()} onProviderAuth={vi.fn()} />
    );
    expect(container.textContent).toContain("Sign In");
    expect(container.textContent).toContain("GitHub");
    expect(container.querySelectorAll("input").length).toBe(2); // email + password
  });
  it("register mode", () => {
    const { container } = render(
      <AuthForm mode="register" providers={[]} onSubmit={vi.fn()} onProviderAuth={vi.fn()} />
    );
    expect(container.textContent).toContain("Create Account");
    expect(container.querySelectorAll("input").length).toBe(3); // name + email + password
  });
  it("provider auth", () => {
    const fn = vi.fn();
    const { container } = render(
      <AuthForm mode="login" providers={[{ id: "github", label: "GitHub" }]}
        onSubmit={vi.fn()} onProviderAuth={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("github");
  });
});
