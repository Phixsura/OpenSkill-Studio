"""Control-plane request/response schemas.

Convention: platform-facing responses may carry cost/margin data; tenant-facing
responses are constructed field-by-field from explicit whitelists and must
never include internal cost, margin, or FX fields (R82 total-fields rule).
"""
