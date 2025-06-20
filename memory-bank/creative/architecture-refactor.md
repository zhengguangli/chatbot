# 🎨 CREATIVE PHASE: Architecture Design

## 1. Problem Statement
The current project structure is cluttered and has several overlapping modules, making it difficult to maintain and extend. Key issues include multiple entry points, duplicated logic in `interfaces` and `services`, and an unorganized UI layer. The goal is to refactor the project into a clean, layered architecture that is modular, scalable, and easy to understand.

## 2. Architecture Decision
A layered architecture with Dependency Injection (via a Service Container) was chosen. This pattern provides a clear separation of concerns, improves testability, and reduces coupling between components.

- **UI Layer**: Handles user interaction (CLI, Streamlit).
- **Application Layer**: Contains the core business logic, managed and served by a central Service Container.
- **Core/Data Layer**: Manages data models, external API communication, and configuration.

## 3. Target Architecture Diagram
This diagram visualizes the relationships and dependencies between the major components of the refactored application.

```mermaid
graph TD
    subgraph " "
        direction LR
        subgraph "UI Layer"
            direction TB
            CLI["CLI (ui/cli.py)"]
            Streamlit["Streamlit (ui/streamlit.py)"]
        end

        subgraph "Application Layer"
            direction TB
            Container["Service Container<br>(services/service_container.py)"]
            MessageHandler["Message Handler<br>(services/message_handler.py)"]
            SessionManager["Session Manager<br>(services/session_manager.py)"]
            StorageService["Storage Service<br>(services/storage_service.py)"]
        end

        subgraph "Core/Data Layer"
            direction TB
            Models["Data Models<br>(core/models.py)"]
            Client["API Client<br>(core/client.py)"]
            Config["App Config<br>(config/settings.py)"]
        end

        Launcher["Launcher<br>(launcher/core.py)"]

        %% UI to App
        CLI --> Container
        Streamlit --> Container

        %% App Layer Dependencies
        Container --> MessageHandler
        Container --> SessionManager
        Container --> StorageService
        MessageHandler --> SessionManager
        SessionManager --> StorageService

        %% App to Core
        MessageHandler --> Client
        SessionManager --> Models
        StorageService --> Models
        Client --> Config
        
        %% Launcher Dependencies
        Launcher --> Container
        Launcher --> Config
    end

    style Launcher fill:#8D33FF,stroke:#000,color:white
    style UI fill:#33B5E5,stroke:#000,color:white
    style Container fill:#FFBB33,stroke:#000,color:black
    style Services fill:#99CC00,stroke:#000,color:black
    style Core fill:#FF4444,stroke:#000,color:white
```

## 4. Implementation Plan
The implementation will follow the five phases outlined in `memory-bank/tasks.md`. This architecture diagram will serve as the guiding blueprint for all refactoring activities in the `BUILD` phase. 