/**
 * Error types for the OpenSkill SDK.
 */

export class OpenSkillError extends Error {
  constructor(
    message: string,
    public code: string = "UNKNOWN_ERROR",
    public statusCode: number = 500,
  ) {
    super(message);
    this.name = "OpenSkillError";
  }
}

export class ApiError extends OpenSkillError {
  constructor(
    message: string,
    code: string,
    statusCode: number,
    public details?: unknown[],
  ) {
    super(message, code, statusCode);
    this.name = "ApiError";
  }
}

export class AuthError extends OpenSkillError {
  constructor(message: string = "Authentication failed") {
    super(message, "AUTH_ERROR", 401);
    this.name = "AuthError";
  }
}

export class NotFoundError extends OpenSkillError {
  constructor(message: string = "Resource not found") {
    super(message, "NOT_FOUND", 404);
    this.name = "NotFoundError";
  }
}

export class RateLimitError extends OpenSkillError {
  constructor(
    public retryAfter: number = 60,
    message: string = "Rate limit exceeded",
  ) {
    super(message, "RATE_LIMITED", 429);
    this.name = "RateLimitError";
  }
}

export class ValidationError extends OpenSkillError {
  constructor(
    message: string,
    public details?: unknown[],
  ) {
    super(message, "VALIDATION_ERROR", 422);
    this.name = "ValidationError";
  }
}
