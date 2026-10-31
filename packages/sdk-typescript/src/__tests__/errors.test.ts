import { describe, test, expect } from "vitest";
import {
  OpenSkillError,
  ApiError,
  AuthError,
  NotFoundError,
  RateLimitError,
  ValidationError,
} from "../errors.js";

describe("Error hierarchy", () => {
  test("OpenSkillError has code and statusCode", () => {
    const err = new OpenSkillError("test", "TEST", 500);
    expect(err.message).toBe("test");
    expect(err.code).toBe("TEST");
    expect(err.statusCode).toBe(500);
    expect(err.name).toBe("OpenSkillError");
  });

  test("ApiError extends OpenSkillError", () => {
    const err = new ApiError("api fail", "API_ERR", 400, ["d1"]);
    expect(err).toBeInstanceOf(OpenSkillError);
    expect(err.name).toBe("ApiError");
    expect(err.details).toEqual(["d1"]);
  });

  test("AuthError defaults to 401", () => {
    const err = new AuthError();
    expect(err.statusCode).toBe(401);
    expect(err.code).toBe("AUTH_ERROR");
  });

  test("NotFoundError defaults to 404", () => {
    const err = new NotFoundError();
    expect(err.statusCode).toBe(404);
  });

  test("RateLimitError has retryAfter", () => {
    const err = new RateLimitError(30);
    expect(err.statusCode).toBe(429);
    expect(err.retryAfter).toBe(30);
  });

  test("ValidationError has details", () => {
    const err = new ValidationError("invalid", [{ field: "name" }]);
    expect(err.statusCode).toBe(422);
    expect(err.details).toHaveLength(1);
  });
});
