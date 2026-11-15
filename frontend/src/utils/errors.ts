/**
 * Extracts a clear human-readable error message from an API error response.
 * Handles:
 * 1. backend global error handler format: { success: false, message: "...", errors: [...] }
 * 2. standard FastAPI HTTPException format: { detail: "..." }
 * 3. Axios or network error: error.message
 */
export function getErrorMessage(err: any, defaultMessage: string = 'An error occurred'): string {
  if (!err) return defaultMessage;

  const data = err.response?.data;
  if (data) {
    // 1. If global error handler returned a message
    if (typeof data.message === 'string' && data.message.trim()) {
      // If validation errors are attached, include the first one for clarity
      if (Array.isArray(data.errors) && data.errors.length > 0) {
        const firstErr = data.errors[0];
        if (firstErr?.message) {
          return `${data.message} (${firstErr.field ? firstErr.field + ': ' : ''}${firstErr.message})`;
        }
      }
      return data.message;
    }

    // 2. If standard FastAPI detail string
    if (typeof data.detail === 'string' && data.detail.trim()) {
      return data.detail;
    }

    // 3. If detail is an array (e.g. raw FastAPI validation errors)
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      const first = data.detail[0];
      return first?.msg || first?.message || defaultMessage;
    }
  }

  // Fallback to error message or default
  return err.message || defaultMessage;
}
