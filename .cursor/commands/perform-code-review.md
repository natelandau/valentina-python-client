# Perform Code Review

## Overview

Perform a code review of the current file to ensure it is clean, readable, and follows best practices.

## Steps

1. **Understand the file**
    - Read the code of the file to understand the purpose and functionality.
    - Read associated files only if necessary to understand the context.
    - Note any assumptions or questions to clarify with the author
2. **Validate functionality**
    - Confirm the code delivers the intended behavior
    - Exercise edge cases or guard conditions mentally or by running locally
    - Check error handling paths and logging for clarity
    - Edge cases and guard conditions are handled gracefully.
3. **Assess quality**
    - Ensure functions are focused, names are descriptive, and code is readable
    - Watch for duplication and dead code
    - Verify docstrings and inline comments are up to date and accurate.
4. **Review security and risk**
    - Look for injection points, insecure defaults, or missing validation
    - Confirm secrets or credentials are not exposed
    - Evaluate performance or scalability impacts of the change
5. **Review performance and scalability**
    - Follows performance best practices for the framework
    - Proper data prefetching/caching strategies used
    - Optimization techniques applied appropriately
    - Memory usage is optimized
    - Dependencies and bundle size considered

## Review Checklist

### Functionality

-   [ ] Intended behavior works and matches requirements
-   [ ] Edge cases handled gracefully
-   [ ] Error handling is appropriate and informative

### Code Quality

-   [ ] Code structure is clear and maintainable
-   [ ] No unnecessary duplication or dead code

### Security & Safety

-   [ ] No obvious security vulnerabilities introduced
-   [ ] Inputs validated and outputs sanitized
-   [ ] Sensitive data handled correctly

### Performance and Scalability

-   [ ] Follows performance best practices for the framework
-   [ ] Proper data prefetching/caching strategies used
-   [ ] Optimization techniques applied appropriately
-   [ ] Memory usage is optimized
-   [ ] Dependencies and bundle size considered

## Additional Review Notes

-   Architecture and design decisions considered
-   Performance bottlenecks or regressions assessed
-   Coding standards and best practices followed
-   Resource management, error handling, and logging reviewed
-   Suggested alternatives, additional test cases, or documentation updates captured

Provide constructive feedback with concrete examples and actionable guidance for the author.
