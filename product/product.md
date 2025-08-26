# Product Requirements: Trader-Agent

**Author:** Agentic AI Developer
**Version:** 1.0
**Date:** August 26, 2025

## 1. Introduction

This document outlines the product and technical specifications for **Trader-Agent**, a generative UX AI agent designed to assist users in stock trading. The agent will provide a conversational interface (chatbox) for users to visualize market data, screen for stocks, receive recommendations, and execute mock trades. The core objective is to create a seamless, end-to-end product experience, including user history and session management, within a two-week development timeline for an MVP.

## 2. Core Features

The Trader-Agent will be composed of several specialized agents to handle distinct tasks. The primary user-facing features are:

1.  **Data Visualization**: Dynamically generate and display charts for specific stocks based on user prompts.
2.  **Stock Screening**: Screen and list stocks based on user-defined criteria such as industry, sector, or performance metrics.
3.  **Stock Recommendation**: Provide buy or sell recommendations based on a predefined logic using technical indicators.
4.  **Mock Buying**: Simulate the purchase of a stock upon user consent and update a mock portfolio.
5.  **Mock Selling**: Simulate the sale of a stock upon user consent and update a mock portfolio.

## 3. Technical Architecture

### 3.1 Tech Stack

*   **Backend**:
    *   **Framework**: FastAPI
    *   **Database**: PostgreSQL
*   **Frontend**:
    *   **Framework**: React + Vite
    *   **Styling**: Tailwind CSS
*   **AI/ML & Libraries**:
    *   **Agent Logic**: Google AI SDK
    *   **UI Generation**: `ai-sdk` or `v0` for generative UI components.
    *   **LLM Providers**: External LLM APIs (e.g., OpenAI, Google Gemini) will be used for code generation and natural language understanding. No custom model training is required.

### 3.2 System Architecture

The system will be built on a client-server model.

*   The **React frontend** will provide the chat interface and render dynamic visualizations.
*   The **FastAPI backend** will host the agentic logic, manage API endpoints, handle database interactions, and orchestrate calls to external LLMs and data APIs.
*   **PostgreSQL** will store user data, chat history, and mock portfolio transactions to ensure persistence across sessions.
*   A **Runner Service** will be responsible for interpreting user prompts, routing tasks to the appropriate agent, and managing the overall workflow.
*   **State and Session Management** will be implemented to track the conversation context and user session data, allowing users to log in and resume their activities.

## 4. Agent-based Architecture

The core logic is modularized into five distinct agents, each with a specific role. These agents can work in sequence to create a generative UX flow or be invoked in parallel based on the user's prompt.

### 4.1 Visualizer Agent

*   **Role**: To fetch and visualize stock data.
*   **Trigger**: A user prompt like, *"Generate a graph of Tata Motors' performance for the first quarter of 2025."*
*   **Flow**:
    1.  Parse the user's prompt to identify the stock ticker, metric, and time frame.
    2.  Call an external/internal API to fetch the required financial data.
    3.  Feed the data and the visualization requirement to an external LLM.
    4.  The LLM generates the necessary code (e.g., React component) for the chart.
    5.  The generated code is rendered on the frontend to display a dynamic data visualization.

### 4.2 Screening Agent

*   **Role**: To screen and list stocks based on specified criteria.
*   **Triggers**:
    1.  **Generative UX Flow**: After the Visualizer Agent displays a chart, this agent can proactively ask the user if they want to see the top 5 performing stocks from the same industry.
    2.  **Direct Prompt**: A user prompt like, *"Screen the top 5 performing stocks from the automotive sector."*
*   **Flow**:
    1.  Identify the industry/sector and screening criteria from the prompt or previous context.
    2.  Call a tool or external API to fetch the list of stocks that meet the criteria.
    3.  Display the results in the frontend.
    4.  Prompt the user for the next action, such as getting a recommendation or visualizing one of the screened stocks.

### 4.3 Recommendation Agent

*   **Role**: To provide buy or sell recommendations for stocks.
*   **Triggers**:
    1.  **Sequential Flow**: Triggered after the Screening Agent provides a list of stocks.
    2.  **Direct Prompt**: A user prompt like, *"Recommend 5 stocks to buy in the technology industry."*
*   **Flow**:
    1.  For each target stock, fetch data for key technical indicators (e.g., RSI, Volume, Moving Average).
    2.  Apply a predefined trading strategy logic. For example, a "buy" signal might be triggered if at least two of the three indicators are positive (e.g., RSI < 30, Volume > Average, and Price > 50-day MA).
    3.  Rank the stocks based on the strength of the buy/sell signal.
    4.  Present the ordered list of recommendations to the user, clearly labeling them as "Buy" or "Sell" opportunities.
    5.  Prompt the user for consent to execute a mock trade.

### 4.4 Buyer Agent

*   **Role**: To execute a mock stock purchase.
*   **Triggers**:
    1.  **Post-Recommendation**: The user consents to buy a stock from the list provided by the Recommendation Agent.
    2.  **Direct Prompt**: A user prompt like, *"Buy 150 quantity of XYZ stock."*
*   **Flow**:
    1.  Parse the stock ticker and quantity from the prompt.
    2.  Record the "buy" transaction in the PostgreSQL database, including the stock, quantity, and mock execution price/time.
    3.  Display a success message to the user confirming the mock purchase.

### 4.5 Seller Agent

*   **Role**: To execute a mock stock sale.
*   **Triggers**:
    1.  **Post-Recommendation**: The user consents to sell a stock from the list provided by the Recommendation Agent.
    2.  **Direct Prompt**: A user prompt like, *"Sell 150 quantities of XYZ stock."*
*   **Flow**:
    1.  Parse the stock ticker and quantity from the prompt.
    2.  Record the "sell" transaction in the PostgreSQL database.
    3.  Display a success message to the user confirming the mock sale.

## 5. User Workflows

### 5.1 Scenario A: Sequential Generative UX Flow

1.  **User**: "Plot a graph for Tata Motors this quarter's performance."
2.  **Visualizer Agent**: Fetches data and displays the chart on the frontend.
3.  **System (Generative UX)**: "Would you like to see the top 5 performers from the automotive industry?"
4.  **User**: "Yes."
5.  **Screening Agent**: Lists the top 5 stocks.
6.  **System (Generative UX)**: "Would you like a buy or sell recommendation for any of these stocks?"
7.  **User**: "Yes, for all of them."
8.  **Recommendation Agent**: Analyzes the stocks using technical indicators and presents an ordered list of buy/sell opportunities.
9.  **System (Generative UX)**: "Would you like to execute a mock trade for any of these recommendations?"
10. **User**: "Buy 10 shares of the top recommended stock."
11. **Buyer Agent**: Executes the mock purchase and confirms with a success message.

### 5.2 Scenario B: Direct Agent Invocation

The user can bypass the sequential flow and directly trigger any agent:

*   **Direct Buy/Sell**: The user prompts, *"Buy 100 shares of AAPL,"* which directly triggers the **Buyer Agent**.
*   **Direct Recommendation**: The user prompts, *"Give me buy recommendations in the pharma sector,"* which directly triggers the **Recommendation Agent**.
*   **Direct Screening**: The user prompts, *"Show me the most volatile stocks today,"* which directly triggers the **Screening Agent**.

## 6. MVP Development Plan (2-Week Timeline)

### Week 1: Backend, Core Logic, and Agent Setup

*   **Day 1-2**: Project setup. Initialize FastAPI backend, React frontend, and PostgreSQL database. Define basic API routes and database schema (for users, history, portfolio).
*   **Day 3-4**: Implement User Authentication and Session Management. Create DB session services.
*   **Day 5-6**: Develop the core logic for each agent.
    *   **Visualizer/Screening**: Integrate with a financial data API (e.g., Alpha Vantage, Finnhub).
    *   **Recommendation**: Define and implement the initial trading strategy logic.
    *   **Buyer/Seller**: Create the mock transaction logic.
*   **Day 7**: Set up the main **Runner** to orchestrate agent calls based on basic prompt parsing.

### Week 2: Frontend, Integration, and Deployment

*   **Day 8-9**: Develop the frontend UI. Build the chat interface, and components for displaying lists and charts.
*   **Day 10-11**: Integrate the frontend with the backend APIs. Implement dynamic rendering of visualizations generated by the Visualizer Agent (using `v0` or similar).
*   **Day 12**: End-to-end testing of both sequential and direct invocation workflows.
*   **Day 13**: Refinement, bug fixing, and documentation cleanup.
*   **Day 14**: Prepare MVP for demonstration.

## 7. SOLID Principles & Best Practices

The architecture will adhere to SOLID principles:

*   **Single Responsibility Principle**: Each agent has one clear responsibility (e.g., visualizing, screening).
*   **Open/Closed Principle**: The system is open for extension (new agents or strategies can be added) but closed for modification (existing agent logic remains stable).
*   **Liskov Substitution Principle**: All agents will conform to a base agent interface, allowing the runner to use them interchangeably.
*   **Interface Segregation Principle**: Agents will not depend on methods they do not use.
*   **Dependency Inversion Principle**: High-level modules (the runner) will depend on abstractions (base agent class), not on low-level implementations (specific agents).
