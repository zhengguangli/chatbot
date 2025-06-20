# Technical Context

> **Purpose**: Technical implementation details, dependencies, and environment setup.

## Development Environment
- **OS**: macOS (Darwin)
- **Shell**: /usr/local/bin/zsh
- **Working Directory**: /Users/lizhengguang/Desktop/chatbot
- **Python Version**: >= 3.9 required

## Dependencies
- **Package Manager**: UV
- **Core Dependencies**:
  - openai >= 1.88.0
  - langchain >= 0.3.25
  - streamlit >= 1.46.0
  - watchdog >= 6.0.0
  - dotenv >= 0.9.9
- **Dev Dependencies**:
  - black >= 25.1.0
  - pytest >= 8.4.1

## Build Configuration
- To be defined during technical setup

## Environment Variables
- To be documented as needed

## API Endpoints
- To be defined for API-based projects

## Database Schema
- To be designed if database is required

## Testing Strategy
- To be established during planning phase

## Deployment Configuration
- To be defined based on deployment target

## Project Structure
- `src/` - Main source directory
  - `core/` - Core chatbot functionality
  - `ui/` - User interface modules (streamlit & CLI)
  - `config/` - Configuration management
  - `utils/` - Utility functions
- `main.py` - Entry point
- `pyproject.toml` - Project configuration 