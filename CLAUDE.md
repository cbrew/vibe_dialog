# Claude Helper Guidelines

## Project Commands
- **Build**: `npm run build`
- **Dev Server**: `npm run dev`
- **Lint**: `npm run lint`
- **Test (all)**: `npm run test`
- **Test (single)**: `npm run test -- -t "test name"`
- **Typecheck**: `npm run typecheck`

## Code Style Guidelines
- **Formatting**: Use Prettier with default settings
- **Naming**: 
  - camelCase for variables and functions
  - PascalCase for classes and components
  - snake_case for database fields
- **Imports**: Group by external/internal, sort alphabetically
- **Types**: Use TypeScript with explicit return types on functions
- **Error Handling**: Use try/catch with custom error classes
- **Comments**: Document complex logic, no comments for obvious code
- **Components**: One component per file, follow React best practices
- **State Management**: Use React Context API for global state

## Repository Structure
The repository is a newly initialized project called "vibe_dialog".