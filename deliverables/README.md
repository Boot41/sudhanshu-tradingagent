# Trader-Agent 🤖📈

A generative AI-powered trading assistant that provides conversational stock analysis, screening, recommendations, and mock trading capabilities through an intuitive chat interface.

## 🎯 Overview

Trader-Agent is a sophisticated multi-agent system designed to assist users in stock trading through natural language interactions. The system combines real-time market data, technical analysis, and AI-powered insights to deliver a seamless trading experience with mock portfolio management.

### Key Features

- **📊 Data Visualization**: Generate dynamic charts and graphs for stock performance analysis
- **🔍 Stock Screening**: Filter and discover stocks based on custom criteria (sector, performance, volatility)
- **💡 AI Recommendations**: Get buy/sell recommendations using technical indicators and trading strategies
- **💰 Mock Trading**: Execute simulated trades with portfolio tracking and transaction history
- **🔐 User Authentication**: Secure login system with JWT-based session management
- **💬 Conversational Interface**: Natural language chat interface for all trading operations

## 🏗️ Architecture

### Tech Stack

**Backend**
- **Framework**: FastAPI with Python 3.10+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: Google AI SDK, Google Gemini, OpenAI, Groq
- **Authentication**: JWT with bcrypt password hashing
- **Data Sources**: Yahoo Finance (yfinance), Financial APIs

**Frontend**
- **Framework**: React 18 + TypeScript + Vite
- **UI Library**: Radix UI components with Tailwind CSS
- **State Management**: Zustand + React Query
- **Charts**: Recharts for data visualization
- **Routing**: React Router DOM

### Agent-Based System

The application uses a modular agent architecture with specialized components:

1. **🎨 Visualizer Agent**: Fetches and renders stock charts and performance data
2. **🔎 Screening Agent**: Filters stocks based on user-defined criteria
3. **🎯 Recommendation Agent**: Analyzes stocks using technical indicators (RSI, Moving Averages, Volume)
4. **💳 Buyer Agent**: Executes mock purchase transactions
5. **💸 Seller Agent**: Handles mock sale transactions
6. **🎭 Orchestrator**: Coordinates agent interactions and manages conversation flow

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 12+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd tradingagent
```

2. **Backend Setup**
```bash
cd server

# Install dependencies using uv (recommended) or pip
uv pip install -e .
# OR
pip install -e .

# Copy environment template and configure
cp .env.example .env
# Edit .env with your API keys and database credentials
```

3. **Frontend Setup**
```bash
cd client/web

# Install dependencies
pnpm install
# OR
yarn install
```

4. **Database Setup**
```bash
# Create PostgreSQL database
createdb tradingagent

# Run migrations (if using Alembic)
cd server
alembic upgrade head
```

### Environment Configuration

Create a `.env` file in the `server/` directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/tradingagent

# API Keys
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gemini-pro

# JWT Security
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ADK Web Server (if using Google ADK)
ADK_WEB_PORT=8001

# Application
ENVIRONMENT=development
DEBUG=true
```

### Running the Application

1. **Start the Backend Server**
```bash
cd server
source .venv/bin/activate (activate your virtual environment)
uvicorn main:app --reload --port 8000
```

2. **Start the Frontend Development Server**
```bash
cd client/web
pnpm run dev
```

3. **Start Google ADK Web Server** (if configured)
```bash
cd server
adk web
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ADK Web: http://localhost:8000

## 📖 Usage Examples

### Sequential Workflow
```
User: "Plot a graph for Tesla's performance this quarter"
→ Visualizer Agent displays TSLA chart
→ System: "Would you like to see top 5 EV stocks?"
→ User: "Yes"
→ Screening Agent shows top performers
→ System: "Want buy/sell recommendations?"
→ User: "Yes, for all of them"
→ Recommendation Agent analyzes and ranks stocks
→ User: "Buy 10 shares of the top recommendation"
→ Buyer Agent executes mock trade
```

### Direct Commands
- `"Buy 100 shares of AAPL"` - Direct purchase (not implemented)
- `"Show me volatile tech stocks today"` - Direct screening (not implemented)
- `"Give me pharma sector recommendations"` - Direct analysis (implemented with mock data)
- `"Sell 50 shares of TSLA"` - Direct sale (not implemented)

## 🛠️ Development

### Project Structure
```
tradingagent/
├── client/web/                 # React frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Route components
│   │   └── lib/              # Utilities and API clients
│   └── package.json
├── server/                    # FastAPI backend
│   ├── agent/                # Agent implementations
│   ├── api/                  # API route handlers
│   ├── core/                 # Configuration and security
│   ├── db/                   # Database models and connections
│   ├── schemas/              # Pydantic models
│   ├── service/              # Business logic services
│   └── pyproject.toml
└── product/                  # Documentation
    ├── product.md           # Product requirements
    └── arch.md             # Architecture documentation
```

### Development Commands

**Backend**
```bash
# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest

# Format code
black .
ruff check .

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

**Frontend**
```bash
# Development server
pnpm run dev

# Build for production
pnpm run build

# Lint code
pnpm run lint

# Preview production build
pnpm run preview
```

### API Endpoints

**Authentication**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

**Chat & Trading**
- `POST /api/chat/message` - Send chat message to agents
- Other endpoints will be added in future releases

## 🔒 Security Features

- JWT-based authentication with token blacklisting
- Password hashing using bcrypt
- CORS protection
- SQL injection prevention via SQLAlchemy ORM
- Environment-based configuration management

## 🧪 Testing (not implemented yet)

```bash
# Backend tests
cd server
pytest tests/

# Frontend tests
cd client/web
npm test
```

## 📦 Deployment

### Production Build

1. **Backend**
```bash
cd server
pip install -e .
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. **Frontend**
```bash
cd client/web
npm run build
# Serve the dist/ folder with your preferred web server
```

### Docker Support

```dockerfile
# Example Dockerfile for backend
FROM python:3.10-slim
WORKDIR /app
COPY server/ .
RUN pip install -e .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow SOLID principles in architecture design
- Write comprehensive tests for new features
- Use type hints in Python code
- Follow React best practices and hooks patterns
- Maintain consistent code formatting

## 🙋‍♂️ Support

For questions, issues, or contributions:

- **Author**: Sudhanshu Sinha
- **Email**: sudhanshu.sinha@think41.com
- **Project Issues**: [GitHub Issues](link-to-issues)

## 🗺️ Future Scalability Prospects

- [ ] Real-time market data streaming
- [ ] Advanced technical indicators
- [ ] Portfolio performance analytics
- [ ] Social trading features
- [ ] Mobile app development
- [ ] Integration with real brokers (paper trading)
- [ ] Advanced risk management tools

---

**⚠️ Disclaimer**: This application is for educational and demonstration purposes only. All trades are simulated and no real money is involved. Always consult with financial advisors before making real investment decisions.
