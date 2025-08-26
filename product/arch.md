# Architecture: Trader-Agent

**Author:** Agentic AI Developer
**Version:** 1.0
**Date:** August 26, 2025

## 1. Introduction

This document provides a detailed overview of the technical architecture for **Trader-Agent**, a generative UX AI agent for stock trading. It outlines the system components, their interactions, the technology stack, and the design principles guiding development. This architecture is designed to support the features and workflows defined in the `product.md`.

## 2. High-Level Architecture Overview

Trader-Agent is built on a modular, agent-based, client-server architecture.

*   A **React-based frontend** provides the user interface, primarily a chatbox, and renders dynamic content like charts.
*   A **FastAPI backend** serves as the application's core, hosting the agentic logic, managing state, and interacting with the database and external services.
*   A **PostgreSQL database** ensures data persistence for user information, conversation history, and mock portfolio transactions.
*   **External AI/Data services** are leveraged for LLM-driven code generation (for UI) and for fetching real-time financial data.

The system is designed for both sequential, generative workflows and direct, parallel agent execution based on user prompts.

## 3. Technology Stack

| Component      | Technology/Library                                                              | Purpose                                                    |
| :------------- | :------------------------------------------------------------------------------ | :--------------------------------------------------------- |
| **Backend**    | FastAPI                                                                         | High-performance API development and agent orchestration.  |
| **Frontend**   | React + Vite                                                                    | Building a fast, modern, and reactive user interface.      |
| **Styling**    | Tailwind CSS                                                                    | Utility-first CSS framework for rapid UI development.      |
| **Database**   | PostgreSQL                                                                      | Relational data storage for users, history, and portfolios. |
| **Agent Logic**| Google AI SDK                                                                   | Framework for building and managing the AI agents.         |
| **UI Generation**| `ai-sdk` or `v0`                                                                | Dynamically generating frontend UI components from LLMs.   |
| **LLM Providers**| External APIs (e.g., OpenAI, Google Gemini)                                     | Natural language understanding and UI code generation.     |

## 4. System Components

### 4.1 Frontend Architecture

*   **Client Application**: A Single Page Application (SPA) built with React and Vite.
*   **Core UI**: The main interface will be a chatbox that handles user input and displays responses from the agent.
*   **Dynamic Rendering**: The frontend will be capable of rendering dynamic components (e.g., charts, tables) generated on-the-fly by the backend agents and LLMs. It will receive component code or structured data from the backend and display it within the chat flow.
*   **State Management**: Client-side state management will handle the conversation flow and UI state.

### 4.2 Backend Architecture

The backend is built around a central runner that orchestrates multiple specialized agents.

*   **API Layer (FastAPI)**: Exposes RESTful endpoints for the frontend to communicate with. This includes endpoints for sending messages, fetching history, and managing user sessions.
*   **Runner Service**: This is the central brain of the backend. Its responsibilities include:
    *   Receiving and parsing the user's prompt.
    *   Determining the user's intent.
    *   Routing the request to the appropriate agent or sequence of agents.
    *   Managing the overall workflow and conversation state.
*   **State and Session Management**: A dedicated service to track the user's session, conversation context, and authentication status. This allows for persistent conversations, enabling a user to log out and log back in to resume their session.
*   **DB Session Service**: Manages database connections and transactions to ensure data integrity. It provides a clean interface for agents to interact with the PostgreSQL database.

### 4.3 Database Schema

The PostgreSQL database will contain the following key tables:

*   `users`: Stores user credentials and profile information.
*   `chat_history`: Logs the entire conversation history for each user, including prompts and agent responses.
*   `mock_portfolio`: Records all mock buy/sell transactions for each user, tracking their virtual holdings.
*   `sessions`: Manages active user sessions for state persistence.

## 5. Agent-Based Architecture

The core functionality is encapsulated within five distinct agents. The **Runner Service** invokes these agents based on user intent. They can operate independently or be chained together to create a seamless, generative user experience.

*   **`VisualizerAgent`**:
    *   **Input**: User prompt (e.g., "show me a chart of AAPL").
    *   **Process**:
        1.  Parses prompt for stock ticker and parameters.
        2.  Fetches data via a financial data API.
        3.  Constructs a prompt for an external LLM, including the data and a request to generate visualization code (e.g., a React component).
    *   **Output**: Returns the generated UI code to the frontend for rendering.

*   **`ScreeningAgent`**:
    *   **Input**: User prompt (e.g., "find top tech stocks") or context from another agent.
    *   **Process**:
        1.  Parses criteria (sector, industry, metrics).
        2.  Calls a data API or a pre-built tool to filter and retrieve a list of stocks.
    *   **Output**: A list of stocks displayed on the frontend, with a follow-up prompt for the next action.

*   **`RecommendationAgent`**:
    *   **Input**: A list of stocks (from `ScreeningAgent` or user) and a request for recommendation.
    *   **Process**:
        1.  For each stock, fetches technical indicator data (RSI, Volume, MA).
        2.  Applies a predefined trading strategy logic (e.g., if 2/3 indicators are positive, signal a "Buy").
        3.  Ranks stocks based on signal strength.
    *   **Output**: An ordered list of "Buy" or "Sell" recommendations.

*   **`BuyerAgent`**:
    *   **Input**: User consent to buy a specific stock and quantity.
    *   **Process**:
        1.  Parses stock ticker and quantity.
        2.  Records a "buy" transaction in the `mock_portfolio` table in the database.
    *   **Output**: A success confirmation message.

*   **`SellerAgent`**:
    *   **Input**: User consent to sell a specific stock and quantity.
    *   **Process**:
        1.  Parses stock ticker and quantity.
        2.  Records a "sell" transaction in the `mock_portfolio` table.
    *   **Output**: A success confirmation message.

## 6. Design Principles & Best Practices

The architecture is designed following SOLID principles to ensure it is maintainable, scalable, and robust.

*   **Single Responsibility**: Each agent and service has a distinct and singular purpose.
*   **Open/Closed**: The system is designed to be extensible. New agents (e.g., for news sentiment analysis) or new trading strategies can be added without modifying existing code.
*   **Liskov Substitution**: All agents will implement a common interface, allowing the runner to treat them polymorphically.
*   **Interface Segregation**: Agents will only be exposed to the services they need, preventing unnecessary dependencies.
*   **Dependency Inversion**: High-level modules like the Runner will depend on abstractions (agent interfaces), not on concrete implementations, facilitating decoupling and testability.
